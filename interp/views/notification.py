from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from interp.models import Notification
from interp.utils import get_all_notifs, read_this_notif, read_all_notifs

class Notifications(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        all_notifications = Notification.objects.all()
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
