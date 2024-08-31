import errno
import logging
import urllib
import re

from django.http.response import HttpResponseNotFound
from django.forms.models import model_to_dict

from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from trans.models import User
from autotranslate.forms import TranslateRequestForm
from autotranslate.models import UserTranslationQuota
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db import models



import os
import requests
import datetime

from google.cloud import translate


logger = logging.getLogger(__name__)

class AutoTranslateAPI(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
            
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
        
        form = TranslateRequestForm(request.POST)
        if not form.is_valid():
            logging.warning("Invalid Input")
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })
        text = form.cleaned_data["content"]
        input_lang = form.cleaned_data["input_lang"]
        output_lang = form.cleaned_data["output_lang"]

        # Wrap backtick in no-translate blocks
        def replacer(match):
            # Extract the code block content
            block = match.group(1)
            lines = []
            for line in block.split("\n"):
                lines.append(f'<span class="notranslate">{line}</span>')
            # Return the code block with spans wrapped around each line
            return "\n".join(lines)

        text =  re.sub(r'(`+[^`]*`+)', replacer, text, flags=re.MULTILINE)

        if not hasattr(request.user, "usertranslationquota"):
            UserTranslationQuota.objects.create(
                user=request.user, 
                credit=settings.INITIAL_DEFAULT_PER_USER_TRANSLATION_QUOTA)
        
        updated_rows = UserTranslationQuota.objects.filter(user=request.user, credit__gte=len(text)).update(
            credit=models.F('credit') - len(text),
            used=models.F('used') + len(text),
        )
        if updated_rows == 0:
            return JsonResponse({
                "success": False,
                "message": "No Translation Quota. Contact Organizer to Recharge."
            })
        elif updated_rows > 1:
            logging.error("UNEXPECTED PART OF CODE REACHED. THIS SHOULD NOT HAPPEN.")
        try:
            client = translate.TranslationServiceClient.from_service_account_file(
                settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
            response = client.translate_text(
                **{
                    "parent": parent,
                    "contents": ["<pre>" + text + "</pre>"],
                    "mime_type": "text/html",  # mime types: text/plain, text/html
                    "source_language_code": input_lang,
                    "target_language_code": output_lang,
                }
            )

            lines = [translation.translated_text for translation in response.translations]
            translated_text = "\n".join(lines)
            assert translated_text.startswith("<pre>") and translated_text.endswith("</pre>")
            translated_text = translated_text[len("<pre>"):-len("</pre>")]
            
            # Remove no-translate blocks
            translated_text = re.sub(r'<span class="notranslate">(.*?)</span>', r'\1', translated_text, flags=re.MULTILINE)
            return JsonResponse({
                "success": True,
                "message": "",
                "translated_text": translated_text,
                "new_quota": UserTranslationQuota.objects.get(user=request.user).credit
            })
        except Exception as e:
            logging.error("Error in Translation. ", exc_info=e)
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })


