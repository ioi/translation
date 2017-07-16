from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.forms.models import model_to_dict

from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User, Task, Translation, Version, Contest, FlatPage
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.conf import settings

import os, re

from trans.forms import UploadFileForm
from trans.utils import get_translate_edit_permission, can_save_translate, is_translate_in_editing, \
    unleash_edit_token, get_task_by_contest_and_name, get_trans_by_user_and_task, \
    can_user_change_translation, convert_html_to_pdf, add_page_numbers_to_pdf, \
    pdf_response, get_requested_user, add_info_line_to_pdf


class Home(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        home_flat_page_slug = 'home-editor' if user.is_editor() else 'home'
        home_flat_page = FlatPage.objects.filter(slug=home_flat_page_slug).first()
        home_content = home_flat_page.content if home_flat_page else ''
        tasks_by_contest = {contest: [] for contest in Contest.objects.all()}
        for task in Task.objects.order_by('order'):
            if not user.is_editor() and not (task.is_published() and task.contest.public):
                continue
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            frozen = translation and translation.frozen or task.contest.frozen
            tasks_by_contest[task.contest].append(
                {'id': task.id, 'name': task.name, 'is_editing': is_editing, 'frozen': frozen})
        tasks_lists = [{'title': c.title, 'slug': c.slug, 'tasks': tasks_by_contest[c]} for c in
                       Contest.objects.order_by('-order') if
                       len(tasks_by_contest[c]) > 0]
        contests = Contest.objects.order_by('order')
        return render(request, 'home.html', context={'tasks_lists': tasks_lists, 'home_content': home_content,
                                                     'contests': contests, 'is_editor': user.is_editor()})


class Translations(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())
        except Exception as e:
            return HttpResponseBadRequest(e)
        trans = get_trans_by_user_and_task(user, task)
        if trans.frozen or task.contest.frozen or not (task.is_published() or user.is_editor()):
            return HttpResponseForbidden("This task is frozen")
        task_text = task.get_published_text
        contests = Contest.objects.order_by('order')
        return render(request, 'editor.html',
                      context={'trans': trans.get_latest_text(), 'task': task_text,
                               'text_font_base64': user.text_font_base64, 'contest_slug': contest_slug,
                               'contests': contests, 'task_name': task_name, 'is_editor': user.is_editor(),
                               'taskID': task.id, 'language': user.credentials(), 'username': user.username,
                               'language': user.language.code, 'direction': user.language.direction()})


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
        if not can_user_change_translation(user, translation, edit_token) or not (
            task.is_published() or user.is_editor()):
            return JsonResponse({'can_edit': False, 'edit_token': '', 'error': 'forbidden'})
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        translation.add_version(content, saved=saved)
        return JsonResponse({'can_edit': can_edit, 'edit_token': new_edit_token})


class UserFont(View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        return render(request, 'font.css', content_type='text/css', context={'text_font_base64': user.text_font_base64})


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
                content = task.get_published_text
            else:
                translation = get_trans_by_user_and_task(requested_user, task)
                content = translation.get_latest_text()

        return HttpResponse(content, content_type='text/plain; charset=UTF-8')


class TranslationHTML(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name, task_type, pdf_output=False):
        user = User.objects.get(username=request.user)
        requested_user = get_requested_user(request, task_type)
        try:
            task = get_task_by_contest_and_name(contest_slug, task_name, user.is_editor())
        except Exception as e:
            return HttpResponseBadRequest(e)

        if task_type == 'released':
            trans = task.get_base_translation()
            content = task.get_published_text()
        else:
            trans = get_trans_by_user_and_task(requested_user, task)
            content = trans.get_latest_text()

        # TODO check if it's available
        context = {
            'content': content,
            'contest': task.contest.title,
            'task_name': task.name,
            'country': requested_user.country.code,
            'language': requested_user.language.name,
            'language_code': requested_user.language.code,
            'direction': requested_user.language.direction(),
            'username': requested_user.username,
            'pdf_output': pdf_output,
        }
        response = render(request, 'pdf-template.html', context=context)
        response['edit_time'] = trans.get_latest_version().create_time.timestamp()
        return response


class TranslationPDF(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name, task_type):
        requested_user = get_requested_user(request, task_type)
        file_path = '{}/output/{}/{}'.format(settings.MEDIA_ROOT, contest_slug, task_name)
        file_name = '{}-{}.pdf'.format(task_name, requested_user.username)
        pdf_file_path = '{}/{}'.format(file_path, file_name)

        html_response = TranslationHTML().get(request, contest_slug, task_name, task_type, pdf_output=True)
        if not 'edit_time' in html_response:
            return html_response

        last_edit_time = float(html_response['edit_time'])
        rebuild_needed = not os.path.exists(pdf_file_path) or os.path.getmtime(pdf_file_path) < last_edit_time

        if rebuild_needed or 'refresh' in request.GET:
            os.makedirs(file_path, exist_ok=True)
            html = html_response.content.decode("utf-8")
            html = re.sub(r'(href|src)="/', r'\1="{}://{}/'.format(request.scheme, request.get_host()), html)
            convert_html_to_pdf(html, pdf_file_path)
            add_page_numbers_to_pdf(pdf_file_path, task_name)

        return pdf_response(pdf_file_path, file_name)


class TranslationPrint(LoginRequiredMixin, View):
    def post(self, request, contest_slug, task_name, task_type):
        user = User.objects.get(username=request.user)
        pdf_response = TranslationPDF().get(request, contest_slug, task_name, task_type)

        if not 'pdf_file_path' in pdf_response:
            return JsonResponse({'success': False})

        pdf_file_path = pdf_response['pdf_file_path']
        info_line = '{} ({})'.format(user.country.name, user.country.code)
        output_pdf_path = add_info_line_to_pdf(pdf_file_path, info_line)

        # TODO: send pdf file to printer

        os.remove(output_pdf_path)

        return JsonResponse({'success': True})


class AccessTranslationEdit(LoginRequiredMixin, View):
    def post(self, request, id):
        edit_token = request.POST.get('edit_token', '')
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        if not (task.contest.public or user.is_editor):
            return HttpResponseBadRequest("There is no published task")
        translation = Translation.objects.get(user=user, task=task)
        if user != translation.user:
            return HttpResponseForbidden()
        can_edit, new_edit_token = get_translate_edit_permission(translation, edit_token)
        return JsonResponse({'can_edit': can_edit, 'edit_token': new_edit_token, 'content': translation.get_latest_text()})


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
        if user != translation.user or translation.frozen:
            return JsonResponse({'error': 'forbidden'})
        # save last unsaved version if exists
        if not translation.get_latest_version().saved:
            translation.add_version(translation.get_latest_text())
        translation.add_version(content_version.text, 'Revert')
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
        if request.is_ajax():
            return JsonResponse(dict(versions=list(versions_list)))
        return render(request, 'revisions.html', context={'task_name': task.name, 'contest_slug': contest_slug,
                                                          'versions': versions_list, 'direction': direction,
                                                          'task_type': task_type})


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


class PrintCustomFile(LoginRequiredMixin, View):
    def get(self, request):
        form = UploadFileForm()
        return render(request, 'custom-print.html', {'form': form})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest("You should attach a file")
        pdf_file_path = request.FILES['pdf_file_path']
        if not pdf_file_path:
            return HttpResponseBadRequest("You should attach a file")
        # TODO: send pdf file to printer
        pdf_file_path = pdf_file_path.read()
        subject, from_email, to = 'hello', 'navidsalehn@gmail.com', 'navidsalehn@gmail.com'
        text_content = 'Test'
        html_content = '<p>This is an <strong>TEST</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.attach('file.pdf', pdf_file_path, 'application/pdf')
        msg.send()

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
