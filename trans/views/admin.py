from collections import defaultdict

import os
from django.contrib.auth.decorators import permission_required
from django.http.response import HttpResponseBadRequest
from shutil import copyfile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views.generic import View

from django.http import HttpResponseNotFound
from trans.forms import UploadFileForm

from trans.models import User, Task, Translation, Contest, UserContest
from trans.utils import is_translate_in_editing, unleash_edit_token, output_pdf_path, final_pdf_path
from trans.utils.pdf import final_markdown_path
from trans.utils.translation import get_trans_by_user_and_task
from trans.views.translation import TranslationPDF


class AdminCheckMixin(LoginRequiredMixin,object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(AdminCheckMixin, self).dispatch(request, *args, **kwargs)


class StaffCheckMixin(LoginRequiredMixin, object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser or user.groups.filter(name="staff").exists()

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(StaffCheckMixin, self).dispatch(request, *args, **kwargs)


class ISCEditorCheckMixin(LoginRequiredMixin, object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser or user.groups.filter(name="editor").exists()

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(ISCEditorCheckMixin, self).dispatch(request, *args, **kwargs)


class StaffRequiredMixin(LoginRequiredMixin, object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser or user.is_staff

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class UserTranslations(StaffCheckMixin, View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        # tasks = Task.objects.filter(contest__public=True).values_list('id', 'title')
        translations = []
        for task in Task.objects.filter(contest__public=True):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            if translation:
                translations.append((task.id, task.name, True, translation.id, translation.frozen, is_editing))
            else:
                translations.append((task.id, task.name, False, 'None', False, False))
        tasks_by_contest = {contest: [] for contest in Contest.objects.all()}
        for task in Task.objects.filter(contest__public=True, contest__frozen=False).order_by('order'):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            frozen = translation and translation.frozen
            translation_id = translation.id if translation else None
            tasks_by_contest[task.contest].append(
                {'id': task.id, 'name': task.name, 'trans_id': translation_id, 'is_editing': is_editing,
                 'frozen': frozen})
        tasks_lists = [{'title': c.title, 'slug': c.slug, 'id': c.id,
                        'user_contest': UserContest.objects.filter(contest=c, user=user).first(),
                        'tasks': tasks_by_contest[c]} for c in
                       Contest.objects.order_by('-order') if
                       len(tasks_by_contest[c]) > 0]
        can_upload_final_pdf = request.user.has_perm('trans.change_translation')
        form = UploadFileForm()
        return render(request, 'user.html', context={'user_name': username, 'country': user.country.name,
                                                     'tasks_lists': tasks_lists, 'language': user.credentials(),
                                                     'can_upload_final_pdf': can_upload_final_pdf, 'form': form})


class UsersList(StaffCheckMixin, View):
    def get(self, request):
        users = (User.get_translators() | User.objects.filter(username='ISC')).\
            distinct().values('country', 'language', 'username')
        returned_users = []
        user_contest_notes = UserContest.objects.filter(contest__frozen=False).values_list('user__username', 'note')
        user_notes = defaultdict(str)
        for user_name, note in user_contest_notes:
            user_notes[user_name] += note
        for user in users:
            user['is_frozen'] = (user['username'] in user_notes.keys())
            user['frozen_note'] = user_notes[user['username']]
            returned_users.append(user)
        return render(request, 'users.html', context={'users': returned_users})


class AddFinalPDF(StaffCheckMixin, View):
    # @permission_required('trans.change_translation')
    def post(self, request):
        id = request.POST['trans_id']
        trans = Translation.objects.filter(id=id).first()
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest("You should attach a file")

        pdf_file = request.FILES.get('uploaded_file', None)
        if not pdf_file or pdf_file.name.split('.')[-1] != 'pdf':
            return HttpResponseBadRequest("You should attach a pdf file")
        pdf_file_path = final_pdf_path(trans.task.contest.slug, trans.task.name, trans.user)
        with open(pdf_file_path, 'wb') as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        trans.frozen = True
        trans.save()
        return redirect(request.META.get('HTTP_REFERER'))


class FreezeTranslation(StaffCheckMixin, View):
    def post(self, request, id):
        frozen = request.POST.get('freeze', False)
        trans = Translation.objects.filter(id=id).first()
        if trans is None:
            return HttpResponseNotFound("There is no task")
        user = trans.user
        task_type = 'released' if user.username == 'ISC' else 'task'
        contest_slug = trans.task.contest.slug
        task_name = trans.task.name
        if frozen == 'True':
            request.GET = request.GET.copy()
            request.GET['user'] = user.username
            pdf_response = TranslationPDF().get(request, contest_slug, task_name, task_type)
            source_pdf_file_path = output_pdf_path(contest_slug, task_name, task_type, user)
            target_pdf_file_path = final_pdf_path(contest_slug, task_name, user)
            copyfile(source_pdf_file_path, target_pdf_file_path)
            with open(final_markdown_path(contest_slug, task_name, user), 'wb') as f:
                f.write(trans.get_latest_text().encode('utf-8'))
                f.close()
        else:
            if os.path.exists(final_pdf_path(contest_slug, task_name, user)):
                os.remove(final_pdf_path(contest_slug, task_name, user))
            if os.path.exists(final_markdown_path(contest_slug, task_name, user)):
                os.remove(final_markdown_path(contest_slug, task_name, user))
        trans.frozen = (frozen == 'True')
        trans.save()
        return redirect(to=reverse('user_trans', kwargs={'username' : trans.user.username}))


class FreezeUserContest(StaffCheckMixin, View):
    def post(self, request, username, contest_id):
        note = request.POST.get('note', '')
        user = User.objects.get(username=username)
        contest = Contest.objects.filter(id=contest_id).first()
        if contest is None:
            return HttpResponseNotFound("There is no contest")
        user_contest, created = UserContest.objects.get_or_create(contest=contest, user=user)
        user_contest.frozen = True
        user_contest.note = note
        user_contest.save()
        for task in contest.task_set.all():
            get_trans_by_user_and_task(user, task)
        return redirect(to=reverse('user_trans', kwargs={'username': username}))


class UnfreezeUserContest(StaffCheckMixin, View):
    def post(self, request, username, contest_id):
        user = User.objects.get(username=username)
        contest = Contest.objects.filter(id=contest_id).first()
        if contest is None:
            return HttpResponseNotFound("There is no contest")
        UserContest.objects.filter(contest=contest, user=user).delete()
        return redirect(to=reverse('user_trans', kwargs={'username': username}))


class UnleashEditTranslationToken(StaffCheckMixin, View):
    def post(self, request, id):
        trans = Translation.objects.get(id=id)
        if trans is None:
            return HttpResponseNotFound("There is no task")
        unleash_edit_token(trans)
        return redirect(to=reverse('user_trans', kwargs={'username': trans.user.username}))
