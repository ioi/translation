from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
import markdown,pdfkit
import os
import codecs
# Create your views here.
class Home(View):
    def get(self, request, *args, **kwargs):
        print('i am here')
        task = Task.objects.all()
        print(task)
        translations = []
        user = User.objects.get(username=request.user.username)
        for item in task:
            translations.append((item.id, item.title))
        print(translations)
        return render(request, 'questions.html', context={'translations': translations, 'language':str(user.language.name + '-' + user.country.name)})


class Questions(View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        try:
            trans = Translation.objects.get(user=user, task = task)
        except:
            trans = Translation.objects.create(user= user, task = task, language = user.language)

        if user.rtl == True:
            return render(request,'editor-fa.html', context={'trans' : trans.text , 'task' : task.text , 'quesId':id,'language':str(user.language.name + '-' + user.country.name)})
        else :
            return render(request,'editor-eng.html', context={'trans' : trans.text , 'task' : task.text , 'quesId':id, 'language':str(user.language.name + '-' + user.country.name)})

class SaveQuestion(View):
    def post(self,request):
        user = User.objects.get(username=request.user)
        id = request.POST['id']
        content = request.POST['content']
        print(len(content))
        task = Task.objects.get(id=id)
        try:
            ques = Translation.objects.get(user=user,task=task)
            ques.text = content
            ques.save()
        except:
            ques = Translation.objects.create(user = user, task = task, text=content)
            ques.save()
        print('before retrieve')
        print(len(ques.text))
        print('after retrieve')

        q = Translation.objects.get(user=user,task=task)
        print(len(q.text))
        print('in save question')
        version = Version.objects.create(translation=ques, text=content, date_time = datetime.datetime.now() )
        version.save()
        VersionParticle.objects.filter(translation=ques).delete()
        return HttpResponse("done")


class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(to=reverse('task'))

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
        print (request.user.username)
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

class Tasks(View):
    def get(self,request):
        print('i am here')
        ques = Task.objects.all()
        questions = []
        for item in ques:
            questions.append((item.id, item.title))
        user = User.objects.get(username=request.user.username)
        return render(request, 'tasks.html', context={'questions': questions,'language':str(user.language.name + '-' + user.country.name)})

    def post(self,request):
        print(request.POST['title'])
        task = Task.objects.create(text = 'Write Your Question',title = request.POST['title'])
        task.save()
        return redirect(to=reverse('task'))

class EditTask(View):
    def get(self,request,id):
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        return render(request,'editor-task.html', context={'task' : task.text , 'taskId':id,'language':str(user.language.name + '-' + user.country.name)})

class SaveTask(View):
    def post(self,request):
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        task.text = content
        task.save()
        return HttpResponse("done")


class GeneratePDf(View):
    html_text = ''
    def post(self,request):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'line-gap': '2'
        }
        output_file = 'mypdf.pdf'
        print(request.POST['isAdmin'])
        if request.POST['isAdmin'] == 'Yes':
            id = request.POST['TaskId']
            task = Task.objects.get(id=int(id))
            self.html_text = markdown.markdown(task.text, output_format ='html4')
            return render(request,'pdf.html', context={'content':self.html_text,'isAdmin':request.POST['isAdmin'],'taskId':id})

        else:
            id = request.POST['quesId']
            user = User.objects.get(username = request.user.username)
            task = Task.objects.get(id=int(id))
            translation = Translation.objects.get(user=user, task=task)
            self.html_text = markdown.markdown(translation.text, output_format = 'html4')
            self.html_text = """<div style="">""" + self.html_text + "</div>"
            print(self.html_text)
            return render(request,'pdf.html', context={'content':self.html_text,'isAdmin':request.POST['isAdmin'],'taskId':id})
            #pdfkit.from_string(html_text, output_file, options=options)

        file = open(output_file, 'rb')
        response = HttpResponse(file, content_type='application/pdf')
        response['Content   -Disposition'] = 'inline;filename=some_file.pdf'

        return response



class PrintPDf(View):
    html_text = ''
    def html_style(self,user):
        if user.rtl == True:
            self.html_text = """<html dir="rtl"> <head> <meta charset="UTF-8"> <style> h1 { line-height:0} h2 { line-height:0 !important} </style> </head> <body style="white-space:pre-wrap; line-height:1">""" + self.html_text + """</body></html>"""
        else :
            self.html_text = """<html dir="ltr"> <head> <meta charset="UTF-8"> <style> h1 { line-height:0} h2 { line-height:0 !important} </style> </head> <body style="white-space:pre-wrap;line-height:1 ">""" + self.html_text + """</body></html>"""


    def post(self,request):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
        }

        user = User.objects.get(username=request.user.username)
        id = request.POST['TaskId']
        task = Task.objects.get(id=int(id))
        output_file = 'mypdf.pdf'

        print(request.POST['isAdmin'])
        if request.POST['isAdmin'] == 'Yes':
            self.html_text = markdown.markdown(task.text, output_format ='html4',)

        else:
            translation = Translation.objects.get(user=user, task=task)
            self.html_text = markdown.markdown(translation.text, output_format = 'html4')

        file = open(output_file, 'rb')
        # We can add Style to html_text by calling html_style function
        self.html_style(user)
        pdfkit.from_string(self.html_text,output_file,options=options)
        response = HttpResponse(file, content_type='application/pdf')
        response['Content   -Disposition'] = 'inline;filename=some_file.pdf'

        return response


class Versions(View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        try:
            trans = Translation.objects.get(user=user, task = task)
        except:
            trans = Translation.objects.create(user= user, task = task, language = user.language, )

        v = []
        vp = []
        versions = Version.objects.filter(translation=trans).order_by('date_time')
        versionParticles = VersionParticle.objects.filter(translation=trans).order_by('date_time')
        for item in versionParticles:
            vp.append((item.id,item.date_time))
        for item in versions:
            v.append((item.id,item.date_time))
        return render(request,'versions.html', context={'versions' : v , 'versionParticles':vp ,'translation' : trans.text, 'quesId':trans.id})

class GetVersion(View):
    def post(self,request):
        print('in get version ')
        id = request.POST['id']
        version = Version.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class GetVersionParticle(View):
    def post(self,request):
        print('in get version particle ')
        id = request.POST['id']
        version = VersionParticle.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class SaveVersionParticle(View):
    def post(self,request):
        print('in save version particle')
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        user = User.objects.get(username=request.user)
        translation = Translation.objects.get(user=user, task=task)
        if translation.text.strip() == content.strip():
            return HttpResponse("Not Modified")
        versionParticle = VersionParticle.objects.create(translation=translation, text=content, date_time = datetime.datetime.now())
        versionParticle.save()
        translation.text = content
        translation.save()
        print('version particle')
        return HttpResponse("done")

class Notifications(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'notifications.html', context={'notifs': Notification.objects.all().order_by('-pub_date')})
