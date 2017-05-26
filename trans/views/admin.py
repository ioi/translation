from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views.generic import View

from django.http import HttpResponseNotFound, HttpResponse

from trans.models import User, Task, Translation
from trans.utils import StaffCheckMixin, is_translate_in_editing, unleash_edit_translation_token


class UserTranslations(StaffCheckMixin, View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        # tasks = Task.objects.filter(contest__enabled=True).values_list('id', 'title')
        translations = []
        for task in Task.objects.filter(contest__enabled=True):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            if translation:
                translations.append((task.id, task.title, True, translation.id, translation.frozen, is_editing))
            else:
                translations.append((task.id, task.title, False, 'None', False, False))
        return render(request, 'user_translates.html', context={'translations': translations, 'language': user.credentials()})


class UsersList(StaffCheckMixin, View):
    def get(self, request):
        users = User.get_translators()
        return render(request, 'users_list.html', context={'users': users})


class FreezeTranslation(StaffCheckMixin, View):
    def post(self, request, id):
        frozen = request.POST.get('freeze', False)
        trans = Translation.objects.filter(id=id).first()
        if trans is None:
            return HttpResponseNotFound("There is no task")
        trans.frozen = frozen
        trans.save()
        return redirect(to=reverse('user_trans', kwargs={'username' : trans.user.username}))

class UnleashEditTranslationToken(StaffCheckMixin, View):
    def post(self, request, id):
        trans = Translation.objects.get(id=id)
        if trans is None:
            return HttpResponseNotFound("There is no task")
        unleash_edit_translation_token(trans)
        return redirect(to=reverse('user_trans', kwargs={'username': trans.user.username}))
