from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from interp.utils import AdminCheckMixin
from interp.models import Task, User


class Tasks(AdminCheckMixin,View):
    def get(self,request):
        questions = Task.objects.values_list('id', 'title', 'is_published')
        user = User.objects.get(username=request.user.username)
        return render(request, 'tasks.html', context={'questions': questions,'language': user.credentials()})


    def post(self, request):
        title = request.POST['title']
        new_task = Task.objects.create(title=title)
        return redirect(to= reverse('edittask',kwargs = {'id': new_task.id}))


class EditTask(AdminCheckMixin,View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if (task.is_published == False):
            is_published = 'false'
        else:
            is_published = 'true'

        return render(request,'editor-task.html', context={'content' : task.get_latest_text() ,'title':task.title,'is_published':is_published, 'taskId':id,'language':str(user.language.name + '-' + user.country.name)})

class SaveTask(AdminCheckMixin,View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        print(content)
        is_published = request.POST['is_published']
        title = request.POST['title']
        task = Task.objects.get(id=id)
        if(is_published == 'true'):
            task.is_published = True
        task.title = title
        task.save()
        task.add_version(content)
        return HttpResponse("done")


class TaskVersions(LoginRequiredMixin,View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        versions_values = task.versions.all().values('text','create_time')
        return JsonResponse(dict(versions=list(versions_values)))
