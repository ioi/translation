import datetime

from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from trans.models import Notification
from trans.utils import get_all_notifs, read_this_notif, read_all_notifs
from trans.views.admin import StaffRequiredMixin


class ReadNotifications(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        all_notifications = Notification.objects.all().order_by('-create_time')
        if request.is_ajax():
            return JsonResponse(dict(notifications=get_all_notifs(request.user, all_notifications)))
        else:
            return render(request, 'notifications.html',
                          context={'notifications': all_notifications})

    def post(self, request, *args, **kwargs):
        if 'id' in request.POST:
            notif = Notification.objects.filter(id=request.POST['id']).first()
            if notif:
                read_this_notif(request.user, notif)
            else:
                return HttpResponseNotFound('Notification not found')
        elif 'read_all' in request.POST:
            read_all_notifs(request.user)
        else:
            return HttpResponseBadRequest()

        return HttpResponse("Success")


class SendNotification(StaffRequiredMixin, View):
    def post(self, request):
        title = request.POST['title']
        description = request.POST['description']
        notif = Notification(title=title, description=description)
        notif.save()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])