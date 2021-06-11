import os
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from trans.forms import UploadFileForm

from trans.models import User, Translation
from trans.utils.pdf import released_pdf_path, unreleased_pdf_path

from fclist import fclist, fcmatch

class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(to=reverse('admin:index'))
        if request.user.groups.filter(name="staff").exists():
            return redirect(to=reverse('users_list'))

        if request.user.is_authenticated():
            return redirect(to=reverse('home'))
        else:
            return render(request, 'login.html')

class Login(View):
    def post(self, request):
        username = request.POST.get('mail')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)

        if user is not None:
            if remember_me is None:
                self.request.session.set_expiry(0)
            else:
                self.request.session.set_expiry(1209600)

            login(request, user)

            return redirect(to=reverse('firstpage'))

        return render(request, 'login.html', {'login_error': True})


class Settings(LoginRequiredMixin,View):
    def get(self, request):
        user = User.objects.get(username=request.user)
        form = UploadFileForm()
        available_fonts = sorted(set([font.family for font in fclist(fontformat='TrueType')]))
        return render(request, 'settings.html', {'form': form, 'text_font_name': user.text_font_name, 'available_fonts': available_fonts, 'text_family': user.text_family})

    def post(self, request):
        user = User.objects.get(username=request.user.username)

        if 'font_upload' in request.POST:
            form = UploadFileForm(request.POST, request.FILES)
            if not form.is_valid():
                return HttpResponseBadRequest("You should attach a file")
            font_file = request.FILES['uploaded_file']
            if not font_file:
                return HttpResponseBadRequest("You should attach a file")
            import base64
            text_font_base64 = base64.b64encode(font_file.read())
            
            self.__remove_user_related_pdfs(user)
            user.text_font_base64 = text_font_base64
            user.text_font_name = font_file.name
            user.save()
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        elif 'font_select' in request.POST:
            if 'text_family' not in request.POST:
                return HttpResponseBadRequest("You should select a font")

            if not request.POST['text_family']:
                self.__remove_user_related_pdfs(user)
                user.text_family = ''
                user.save()
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

            available_fonts = set([font.family for font in fclist(fontformat='TrueType')])
            if request.POST['text_family'] not in available_fonts:
                return HttpResponseBadRequest("Selected font not available.")
            self.__remove_user_related_pdfs(user)
            user.text_family = request.POST['text_family']
            user.save()

            return HttpResponseRedirect(request.META['HTTP_REFERER'])

    def delete(self, request):
        user = User.objects.get(username=request.user)
        self.__remove_user_related_pdfs(user)
        user.text_font_base64 = ''
        user.text_font_name = ''
        user.save()
        return JsonResponse({'message': "Done"})

    def __remove_user_related_pdfs(self, user):
        for trans in Translation.objects.filter(user=user):
            slug = trans.task.contest.slug
            task_name = trans.task.name
            pdf_paths = [
                released_pdf_path(slug, task_name, user),
                unreleased_pdf_path(slug, task_name, user)
            ]
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

class Logout(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        return redirect(request=request, to=reverse('firstpage'))
