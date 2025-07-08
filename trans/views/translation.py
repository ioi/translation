import errno
import logging

from django.http.response import HttpResponseNotFound
from django.forms.models import model_to_dict

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User, Task, Translation, Version, Contest, Country, FlatPage, UserContest, Contestant, ContestantContest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.urls import reverse

import datetime

from trans.utils.translation import get_translate_edit_permission, can_save_translate, is_translate_in_editing, \
    unleash_edit_token, get_task_by_contest_and_name, get_trans_by_user_and_task, \
    can_user_change_translation, get_requested_user
from trans.utils.pdf import get_file_name_from_path, build_pdf, convert_html_to_pdf, add_page_numbers_to_pdf, \
    pdf_response, build_printed_draft_pdf, render_pdf_template

from print_job_queue import queue

logger = logging.getLogger(__name__)


class Home(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        is_editor = user.is_editor()

        home_flat_page_slug = 'home-editor' if user.is_editor() else 'home'
        home_flat_page = FlatPage.objects.filter(slug=home_flat_page_slug).first()
        home_content = home_flat_page.content if home_flat_page else ''

        if is_editor:
            contests = Contest.objects.order_by('-order')
            contestants = []
        else:
            contests = Contest.objects.filter(public=True).order_by('-order')
            contestants = Contestant.objects.filter(user=user).order_by('code')

        contest_info = {c: {
            'title': c.title,
            'slug': c.slug,
            'id': c.id,
            'tasks': [],
            'user_contest': UserContest.objects.filter(contest=c, user=user).first(),
        } for c in contests}

        for task in Task.objects.filter(contest__in=contests).order_by('order'):
            if not (is_editor or task.is_published()):
                continue
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            frozen = translation and translation.is_editable_by(user)
            translating = translation and translation.translating
            translation_id = translation.id if translation else None
            contest_info[task.contest]['tasks'].append({
                'id': task.id,
                'name': task.name,
                'trans_id': translation_id,
                'is_editing': is_editing,
                'frozen': frozen,
                'translating': translating,
            })

        if not is_editor:
            contest_contestant = {}
            for cc in ContestantContest.objects.filter(contest__in=contests, contestant__in=contestants).select_related('translation_by_user', 'translation_by_user__language', 'translation_by_user__country'):
                contest_contestant[cc.contest, cc.contestant] = cc

            for contest, cinfo in contest_info.items():
                cinfo['contestant_translations'] = contestant_translations = []
                for ctant in contestants:
                    cc = contest_contestant.get((contest, ctant), None)
                    if cc is None:
                        cc = ContestantContest.obtain(ctant, contest, user)
                    tu = cc.translation_by_user
                    if tu:
                        tr = f'{tu.language.name} ({tu.country.name})'
                        if tu == user:
                            tr += ' – your translation'
                    else:
                        tr = None
                    contestant_translations.append((ctant, tr))

        return render(request, 'home.html', context={
            'user': user,
            'contests': contests,   # used by modals.html
            'contest_infos': [ci for ci in contest_info.values() if ci['tasks']],
            'home_content': home_content,
            'is_editor': user.is_editor(),
            'is_onsite': user.is_onsite,
            'is_translating': user.is_translating,
        })


class Healthcheck(View):
    def get(self, request):
        try:
            with open('REVISION', 'r') as f:
                revision = f.read().strip()
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise e
            revision = 'unknown'

        return JsonResponse({'revision': revision})


class Translations(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())
        except Exception as e:
            return HttpResponseBadRequest(e)
        trans = get_trans_by_user_and_task(user, task)
        if trans.is_editable_by(user) or not (task.is_published() or user.is_editor()):
            return HttpResponseForbidden("This task is frozen")
        task_text = task.get_published_text
        contests = Contest.objects.order_by('order')

        return render(request, 'editor.html', context={
            'trans': trans.get_latest_text(),
            'task': task_text,
            'text_font_base64': user.text_font_base64,
            'contest_slug': contest_slug,
            'contests': contests,
            'task_name': task_name,
            'is_editor': user.is_editor(),
            'is_onsite': user.is_onsite,
            'taskID': task.id,
            'language_code': user.language.code,
            'username': user.username,
            'direction': user.language.direction()
        })


class SaveTranslation(LoginRequiredMixin, View):
    def post(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())
        except Exception as e:
            return HttpResponseBadRequest(e)
        translation = get_trans_by_user_and_task(user, task)
        content = request.POST['content']
        saved = request.POST['saved'] == 'true'
        edit_token = request.POST.get('edit_token', '')
        if translation.is_editable_by(user) or not can_user_change_translation(user, translation, edit_token) or not (
                    task.is_published() or user.is_editor()):
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        translation.add_version(content, saved=saved)
        return JsonResponse({'can_edit': can_edit, 'edit_token': new_edit_token})


class UserFont(View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        return render(request, 'font.css', content_type='text/css', context={
            'text_font_base64': user.text_font_base64
        })


class TranslationMarkdown(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name, task_type):
        user = User.objects.get(username=request.user)
        requested_user = get_requested_user(request, task_type)
        version_id = request.GET.get('ver')
        if version_id:
            content_version = Version.objects.filter(id=version_id).first()
            if not content_version.can_view_by(user):
                return None
            content = content_version.text
        else:
            try:
                task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())
            except Exception as e:
                return HttpResponseBadRequest(e)
            if task_type == 'released':
                content = task.get_published_text()
            else:
                translation = get_trans_by_user_and_task(requested_user, task)
                content = translation.get_latest_text()

        return HttpResponse(content, content_type='text/plain; charset=UTF-8')

class TranslationView(LoginRequiredMixin, View):
    def _get_translation_by_contest_and_task_type(self, request, user, contest_slug, task_name, task_type):
        requested_user = get_requested_user(request, task_type)
        task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())

        if task_type == 'released':
            return task.get_base_translation()
        return get_trans_by_user_and_task(requested_user, task)


class TranslationPDF(TranslationView):
    def get(self, request, contest_slug, task_name, task_type):
        user = User.objects.get(username=request.user)
        translation = self._get_translation_by_contest_and_task_type(request, user, contest_slug, task_name, task_type)
        pdf_file_path = build_pdf(translation, task_type)
        return pdf_response(pdf_file_path, get_file_name_from_path(pdf_file_path))


class TranslationPrint(TranslationView):
    def post(self, request, contest_slug, task_name, task_type):
        user = User.objects.get(username=request.user)
        translation = self._get_translation_by_contest_and_task_type(request, user, contest_slug, task_name, task_type)
        pdf_file_path = build_pdf(translation, task_type)

        if translation.user.username == 'ISC':
            info_line = 'Release {}, deliver to {}'.format(translation.get_published_versions_count(), user.country.code)
        else:
            #info_line = 'Printed at {}'.format(translation.get_latest_version().create_time.strftime("%H:%M"))
            info_line = 'Draft printed at {}'.format(datetime.datetime.now().strftime("%H:%M"))
        output_pdf_path = build_printed_draft_pdf(contest_slug, pdf_file_path, info_line)

        queue.enqueue_draft_print_job(output_pdf_path,
                                      print_count=1,
                                      owner=request.user,
                                      owner_country=user.country.code,
                                      group=contest_slug)

        if translation.user == user and user.username != 'ISC':
            translation.save_last_version(release_note='Printed', saved=True)

        return JsonResponse({'success': True})


class AccessTranslationEdit(LoginRequiredMixin, View):
    def post(self, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not (task.contest.public or user.is_editor):
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if translation.is_editable_by(user) or user != translation.user:
            return HttpResponseForbidden()
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        return JsonResponse(
            {'can_edit': can_edit, 'edit_token': new_edit_token, 'content': translation.get_latest_text()})


class FinishTranslate(LoginRequiredMixin, View):
    def post(self, request, id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        trans = Translation.objects.get(user=user, task=task)
        edit_token = request.POST.get('edit_token', '')
        if trans is None:
            return HttpResponseNotFound("There is no task")
        if not can_save_translate(trans, edit_token):
            return HttpResponseForbidden("You don't have acccess")
        unleash_edit_token(trans)
        return JsonResponse({'message': "Done"})


class Revert(LoginRequiredMixin, View):
    def post(self, request):
        version_id = self.request.POST['id']
        content_version = Version.objects.filter(id=version_id).first()
        user = User.objects.get(username=request.user)
        translation = content_version.translation
        if user != translation.user or translation.is_editable_by(user):
            return JsonResponse({'error': 'forbidden'})
        # save last unsaved version if exists
        if not translation.get_latest_version().saved:
            translation.add_version(translation.get_latest_text())
        translation.add_version(content_version.text, 'Reverted')
        return JsonResponse({'message': 'Done'})


class Versions(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name, task_type):
        user = User.objects.get(username=request.user.username)
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        view_all = request.GET.get('view_all', 'false') == 'true'

        trans = get_trans_by_user_and_task(user, task)
        if task_type == 'released':
            user = User.objects.filter(username='ISC').first()
            trans = task.get_base_translation()

        versions_list = []
        versions = trans.version_set.all().order_by('-create_time')
        if task_type == 'released':
            versions = versions.filter(released='True')

        for item in versions:
            if not view_all and not item.saved and len(versions_list) > 0:
                continue
            versions_list.append(model_to_dict(item))

        direction = 'rtl' if user.language.rtl else 'ltr'
        # versions_values = versions.values('id', 'text', 'create_time', 'release_note')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(dict(versions=list(versions_list)))
        return render(request, 'revisions.html', context={
            'task_name': task.name,
            'trans_frozen': trans.frozen,
            'contest_slug': contest_slug,
            'versions': versions_list,
            'direction': direction,
            'task_type': task_type,
            'view_all': view_all,
            'is_editor': user.is_editor(),
        })


class GetVersion(LoginRequiredMixin, View):
    def get(self, request):
        id = request.GET['id']
        version = Version.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if version.translation.user != user:
            return HttpResponseBadRequest()
        return HttpResponse(version.text)


class GetLatestTranslation(LoginRequiredMixin, View):
    def get(self, request, id):
        # id = request.GET['id']
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        trans = Translation.objects.get(user=user, task=task)
        if trans.user != user:
            return HttpResponseForbidden()
        return HttpResponse(trans.get_latest_text())
