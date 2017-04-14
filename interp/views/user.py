from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from interp.models import User

class FirstPage(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect(to=reverse('task'))

        if request.user.is_authenticated():
            return redirect(to=reverse('home'))
        else:
            return render(request, 'login.html')

class Login(View):
    def post(self, request):
        username = request.POST.get('mail')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        # @milad you should probably verify this, it's supposed to login the user
        user = authenticate(username=username, password=password)

        if user is not None:
            if remember_me is None:
                self.request.session.set_expiry(0)
            else:
                self.request.session.set_expiry(1209600)

            login(request, user)

            return redirect(to=reverse('firstpage'))

        return render(request, 'login.html', {'login_error': True})


class Setting(LoginRequiredMixin,View):
    def post(self, request):
        print (request.user.username)
        user = User.objects.get(username=request.user.username)
        if (request.POST.get('rtl') == 'on'):
            user.language.rtl = True
        else:
            user.language.rtl = False
        user.save()
        return redirect(to=reverse('home'))


class Logout(LoginRequiredMixin,View):
    def get(self, request):
        logout(request)
        return redirect(request=request, to=reverse('firstpage'))
