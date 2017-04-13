from django.shortcuts import render
from django.views.generic import View

from interp.models import Notification

class Notifications(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'notifications.html', context={'notifs': Notification.objects.all().order_by('-pub_date')})
