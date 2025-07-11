import errno
import logging
import urllib
import re
import html

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
            content_errors = form.errors.as_data().get("content", None)
            if content_errors is not None and any([error.code == 'required' for error in content_errors]):
                return JsonResponse({
                    "success": False,
                    "message": "Error. Empty input received. Please enter some text to translate."
                })    
            elif form.non_field_errors():
                return JsonResponse({
                    "success": False,
                    "message": "Error. " + "\n".join(form.non_field_errors()) 
                })    
            else:
                logger.warning("Unexpected invalid input.")
                return JsonResponse({
                    "success": False,
                    "message": "Error in Translation. Contact Organizers."
                })
        text = html.escape(form.cleaned_data["content"])
        input_lang = form.cleaned_data["input_lang"]
        output_lang = form.cleaned_data["output_lang"]

        # Wrap backtick, dollar sign and images in no-translate blocks
        def replacer(match):
            if match.group("image_pattern"):
                # Make sure the description gets translated but not the path
                return f'<span class="notranslate">![</span><span class="translate">{match.group("desc")}</span><span class="notranslate">]({match.group("path")})</span>'
            else:
                # Extract the code block content
                block = match.group(1)
                lines = []
                for line in block.split("\n"):
                    lines.append(f'<span class="notranslate">{line}</span>')
                # Return the code block with spans wrapped around each line
                return "\n".join(lines)
        backtick_pattern = r'(`+)[^`]+?\2'
        dollar_math_pattern = r'(\$+)[^\$]+?\3'
        image_pattern = r'(?P<image_pattern>!\[(?P<desc>[^\n\]]*?)\]\((?P<path>[^\n\)]*?)\))'
        text =  re.sub(fr'({backtick_pattern}|{dollar_math_pattern}|{image_pattern})', replacer, text, flags=re.MULTILINE)
        text = text.replace('</span><span class="notranslate">', "")

        if not hasattr(request.user, "usertranslationquota"):
            UserTranslationQuota.objects.create(
                user=request.user, 
                credit=settings.INITIAL_DEFAULT_PER_USER_TRANSLATION_QUOTA)
        
        updated_rows = UserTranslationQuota.objects.filter(user=request.user, credit__gte=models.F('used') + len(text)).update(
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
            print(translated_text, text)
            
            # Remove no-translate blocks
            translated_text = re.sub(r'</span> <span class="translate">(.*?)</span>', r'</span>\1', translated_text, flags=re.MULTILINE)
            translated_text = re.sub(r'<span class="notranslate">(.*?)</span>', r'\1', translated_text, flags=re.MULTILINE)
            new_quota = UserTranslationQuota.objects.get(user=request.user)
            assert new_quota is not None
            return JsonResponse({
                "success": True,
                "message": "",
                "translated_text": html.unescape(translated_text),
                "new_quota": new_quota.credit - new_quota.used,
            })
        except Exception as e:
            logging.error("Error in Translation. ", exc_info=e)
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })


