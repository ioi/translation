import errno
import logging
import urllib

from django.http.response import HttpResponseNotFound
from django.forms.models import model_to_dict

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User, Task, Translation, Version, Contest, Country, FlatPage, UserContest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.conf import settings

import os
import requests
import datetime

from google.cloud import translate


logger = logging.getLogger(__name__)

class AutoTranslateAPI(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        client = translate.TranslationServiceClient.from_service_account_file(settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
        text = "Hello we know $a \leq 20$ and $j_i \leq 20$ but that $a$ is not the same as $j_i$, i.e. $a_i \\ne j_i$"
        previous_text = request.POST["content"]
        input_lang = request.POST["input_lang"]
        output_lang = request.POST["output_lang"]
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [request.POST['content']],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": input_lang,
                "target_language_code": output_lang,
            }
        )

        lines = [translation.translated_text for translation in response.translations]
        translated_text = "\n".join(lines)

        return JsonResponse(dict(translated_text=translated_text))


