from django.conf import settings

from django.conf.urls import url
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    url(r'^autotranslate_api/', AutoTranslateAPI.as_view(), name='auto_translate_api')
]