from django.conf import settings

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    url(r'^draft/$', draft_queue, name='draft_queue'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
