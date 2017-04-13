from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse

from interp.utils import AdminCheckMixin
from interp.models import Task, User



# Here Comes Mixins

# Create your views here.
class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(to=reverse('task'))

        if request.user.is_authenticated():
            return redirect(to=reverse('home'))
        else:
            return render(request, 'home.html')

class Home(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        task = Task.objects.all()
        translations = []
        user = User.objects.get(username=request.user.username)
        for item in task:
            if item.is_published == True:
                translations.append((item.id, item.title))
        return render(request, 'questions.html', context={'translations': translations, 'language':str(user.language.name + '-' + user.country.name)})


class Tasks(LoginRequiredMixin,View):
    def get(self,request):
        ques = Task.objects.all()
        questions = []
        for item in ques:
            if (item.is_published == False):
                is_published = 'false'
            else:
                is_published = 'true'

            questions.append((item.id, item.title,is_published))
        user = User.objects.get(username=request.user.username)
        return render(request, 'tasks.html', context={'questions': questions,'language':str(user.language.name + '-' + user.country.name)})


    def post(self, request):
        id = request.POST['id']
        is_published = request.POST['is_published']
        if(is_published == 'false'):
            is_published = False
        else :
            is_published = True

        task = Task.objects.get(id=id)
        task.is_published = is_published
        task.save()
        return HttpResponse("done")


class AddTask(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'add-task.html')


    def post(self, request):
        title=request.POST['title']
        content = request.POST['content']
        is_published = request.POST['is_published']
        if(is_published == 'false'):
            is_published = False
        else :
            is_published = True

        task = Task.objects.create(title=title, is_published = is_published)
        task.save()
        task.add_version(content)
        return redirect(to=reverse('task'))


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
        if(is_published == 'false'):
            is_published = False
        else :
            is_published = True

        task = Task.objects.get(id=id)
        task.is_published = is_published
        task.title = title
        task.save()
        task.add_version(content)
        return HttpResponse("done")


class TaskVersions(LoginRequiredMixin,View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        versions_values = task.versions.all().values('text','create_time')
        return JsonResponse(dict(versions=list(versions_values)))
