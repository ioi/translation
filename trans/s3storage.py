import re
from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls import url
from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.views.generic import View
from django.utils.encoding import filepath_to_uri
from storages.backends.s3boto3 import S3Boto3Storage

class S3Storage(S3Boto3Storage):
    def url(self, name, parameters=None, expire=None):
        name = self._normalize_name(self._clean_name(name))
        return urljoin(settings.MEDIA_URL, filepath_to_uri(name))

    def s3url(self, name, parameters=None, expire=None):
        return super().url(name, parameters, expire)

class S3Redirector(View):
    def get(self, request, **kwargs):
        response = redirect(default_storage.s3url(kwargs['path']))
        response['X-Accel-Redirect'] = '/s3proxy'
        return response

    @classmethod
    def urlpatterns(cls):
        pattern = r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/'))
        return [
            url(pattern, cls.as_view()),
        ]
