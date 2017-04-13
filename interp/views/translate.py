import datetime
import json

from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from interp.models import User, Task, Translation, Version, VersionParticle
from django.http import HttpResponse


class Questions(LoginRequiredMixin,View):
    def get(self,request,id):
        user = User.objects.get(username=request.user)
        task = Task.objects.get(id=id)
        try:
            trans = Translation.objects.get(user=user, task = task)
        except:
            trans = Translation.objects.create(user= user, task = task, language = user.language, text = task.text)

        return render(request, 'editor.html',
                      context={'trans': trans.text, 'task': task.text, 'rtl': user.language.rtl, 'quesId': id,
                               'language': str(user.language.name + '-' + user.country.name)})


class SaveQuestion(LoginRequiredMixin,View):
    def post(self,request):
        user = User.objects.get(username=request.user)
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        try:
            ques = Translation.objects.get(user=user,task=task)
            ques.text = content
            ques.save()
        except:
            ques = Translation.objects.create(user = user, task = task, text=content)
            ques.save()

        q = Translation.objects.get(user=user,task=task)
        print('in save question')
        version = Version.objects.create(translation=ques, text=content, date_time = datetime.datetime.now() )
        version.save()
        VersionParticle.objects.filter(translation=ques).delete()
        return HttpResponse("done")


class Versions(LoginRequiredMixin,View):
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


class GetVersion(LoginRequiredMixin,View):
    def post(self,request):
        print('in get version ')
        id = request.POST['id']
        version = Version.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class GetVersionParticle(LoginRequiredMixin,View):
    def post(self,request):
        print('in get version particle ')
        id = request.POST['id']
        version = VersionParticle.objects.get(id=id)
        print(version.text)
        return HttpResponse(version.text)

class SaveVersionParticle(LoginRequiredMixin,View):
    def post(self,request):
        print('in save version particle')
        id = request.POST['id']
        content = request.POST['content']
        task = Task.objects.get(id=id)
        print(request.user)
        user = User.objects.get(username=request.user.username)
        translation = Translation.objects.get(user=user, task=task)
        if translation.text.strip() == content.strip():
            return HttpResponse("Not Modified")
        versionParticle = VersionParticle.objects.create(translation=translation, text=content, date_time = datetime.datetime.now())
        versionParticle.save()
        translation.text = content
        translation.save()
        print('version particle')
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

        self.html_text = request.POST['katexhtml']

        output_file = 'mypdf.pdf'
        print(request.POST['isAdmin'])
        if request.POST['isAdmin'] == 'Yes':
            id = request.POST['TaskId']
            task = Task.objects.get(id=int(id))
            #self.html_text = markdown.markdown(task.text, output_format ='html4')
            return HttpResponse(json.dumps({'content':self.html_text,'isAdmin':request.POST['isAdmin'],'taskId':id}))

        else:
            id = request.POST['quesId']
            user = User.objects.get(username = request.user.username)
            task = Task.objects.get(id=int(id))
            translation = Translation.objects.get(user=user, task=task)
            #self.html_text = markdown.markdown(translation.text, output_format = 'html4')
            self.html_text = """<div style="">""" + self.html_text + "</div>"
            print(self.html_text)
            return HttpResponse(json.dumps({'content':self.html_text,'isAdmin':request.POST['isAdmin'],'taskId':id}))

           # return render(request,'pdf.html', context={'content':self.html_text,'isAdmin':request.POST['isAdmin'],'taskId':id})
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
