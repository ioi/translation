import re

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import View

from trans.models import Task, User, Contest
from trans.utils.translation import get_trans_by_user_and_task
from trans.views.admin import EditorCheckMixin


class AddTask(EditorCheckMixin, View):
    def post(self, request):
        name = request.POST['name']
        if not re.fullmatch('[a-zA-Z0-9_]+', name):
            # This is already checked by client JS, so a crude error message is sufficient
            return HttpResponseBadRequest("Invalid task name")

        contest_id = request.POST['contest']
        contest = Contest.objects.filter(id=contest_id).first()
        contest_tasks = Task.objects.filter(contest=contest)
        order = contest_tasks.latest('order').order + 1 if contest_tasks else 1
        new_task, created = Task.objects.get_or_create(name=name, contest=contest, order=order)
        user = User.objects.get(username=request.user.username)
        trans = get_trans_by_user_and_task(user, new_task) # to initiate translation
        trans.add_version('# ' + name.capitalize(), saved=False)
        return redirect(to=reverse('edit', kwargs={'contest_slug': contest.slug, 'task_name': name}))


class ReleaseTask(EditorCheckMixin, View):
    def post(self, request, contest_slug, task_name):
        release_note = request.POST.get('release_note', '')
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        if task.contest.frozen:
            return HttpResponseBadRequest("The task is frozen")
        task.publish_latest(release_note)
        return HttpResponse("done")
