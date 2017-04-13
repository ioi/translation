
from django.views.generic import View
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponse

from interp.models import Notification
from interp.utils import get_all_notifs, read_this_notif, read_all_notifs

class Notifications(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(notifications=get_all_notifs(request.user)))

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
