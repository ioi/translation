import moratab
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
from .models import *

# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        print('i am here')
        ques = Origques.objects.all()
        print(ques)
        questions = []
        for item in ques:
            questions.append((item.id, item.title))

        print(questions)
        return render(request, 'questions.html', context={'questions': questions})


class Questions(View):
    def get(self,request,id):
        print(request.user.username)
        user = User.objects.get(username=request.user)
        print(user)
        origques = Origques.objects.get(id=id)
        question = Question.objects.get(user=user, origques = origques)
        print(origques)

#        if user.rtl == True:
        return render(request,'editor.html', context={'trans' : question.text , 'orig' : origques.text , 'quesId':id})
#        else:
#            return render(request,'editor-eng.html', context={'trans' : question.text , 'orig' : origques.text , 'quesId':id})
class SaveQuestion(View):
    def post(self,request):
        user = User.objects.get(username=request.user)
        id = request.POST['id']
        content = request.POST['content']
        origques = Origques.objects.get(id=id)
        try:
            ques = Question.objects.get(user=user,origques=origques)
            ques.text = content
            ques.save()
        except:
            ques = Question.objects.create(user = user, origques = origques, text=content)
            ques.save()

        return HttpResponse("done")

class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(to=reverse('home'))
        else:
            return render(request, 'home.html')

class Login(View):
    def post(self, request):
        username = request.POST.get('mail')
        password = request.POST.get('password')
        # @milad you should probably verify this, it's supposed to login the user
        print("imm heeerreee")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('firstpage'))

        return render(request, 'home.html', {'login_error': True})


class Setting(View):
    def post(self, request):
        user = User.objects.get(username=request.user.username)
        if (request.POST.get('rtl') == 'on'):
            user.rtl = True
        else:
            user.rtl = False
        user.save()
        return redirect(to=reverse('home'))


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect(request=request, to=reverse('firstpage'))

class Rendered(View):
    def get(self, request):
        return render(request,'rendered.html')
    def post(self, request):
        f = open('interp/static/content_rendered.txt','r')
        content = f.read()
        return HttpResponse(content)