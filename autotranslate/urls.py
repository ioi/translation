from django.conf import settings

from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('autotranslate_api/', AutoTranslateAPI.as_view(), name='auto_translate_api')
]
