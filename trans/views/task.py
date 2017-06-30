from django.core.mail.message import EmailMultiAlternatives
from django.http.response import HttpResponseRedirect, HttpResponseForbidden

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from trans.utils import get_task_by_contest_and_name, is_translate_in_editing, get_trans_by_user_and_task
from trans.models import Task, User, Contest, Translation, ContentVersion
from trans.views.admin import ISCEditorCheckMixin

from wkhtmltopdf.views import PDFTemplateView


class AddTask(ISCEditorCheckMixin, View):
    def post(self, request):
        if request.user.username != "ISC":
            return HttpResponseForbidden("You don't have access to this page")
        name = request.POST['name']
        name = name.replace(' ', '').replace('/','')
        contest_id = request.POST['contest']
        contest = Contest.objects.filter(id=contest_id).first()
        new_task, created = Task.objects.get_or_create(name=name, contest=contest)
        if not created:
            return HttpResponseBadRequest("This task is duplicate")
        user = User.objects.get(username=request.user.username)
        new_trans = get_trans_by_user_and_task(user, new_task)
        return redirect(to=reverse('edit', kwargs={'contest_slug': contest.slug, 'task_name': new_task.name}))


class ReleaseTask(ISCEditorCheckMixin, View):
    def post(self, request, contest_slug, task_name):
        release_note = request.POST.get('release_note', '')
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        if task.frozen:
            return HttpResponseBadRequest("The task is frozen")
        task.publish_latest(release_note)
        return HttpResponse("done")


class TaskVersions(LoginRequiredMixin, View):
    def get(self, request, contest_slug, task_name):
        user = User.objects.get(username=request.user.username)
        released = True
        if user.is_editor():
            released = False
        task = Task.objects.get(name=task_name, contest__slug=contest_slug)
        ISC_translation = task.get_corresponding_translation()
        versions_query = ISC_translation.versions.order_by('-create_time')
        if released:
            versions_query = versions_query.filter(released=True)
        versions_values = versions_query.values('id', 'text', 'create_time', 'release_note')
        if request.is_ajax():
            return JsonResponse(dict(versions=list(versions_values)))
        else:
            return render(request, 'task-revisions.html',
                          context={'task_name': task.name, 'contest_slug': contest_slug,
                                   'versions': versions_values, 'direction': 'ltr'})
