import logging
import re
import html

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from autotranslate import backends
from autotranslate.forms import TranslateRequestForm
from autotranslate.models import UserTranslationQuota
from django.http import JsonResponse
from django.conf import settings
from django.db import models


logger = logging.getLogger(__name__)


class AutoTranslateAPI(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        

        form = TranslateRequestForm(request.POST)
        if not form.is_valid():
            content_errors = form.errors.as_data().get("content", None)
            backend_errors = form.errors.as_data().get("backend", None)
            if content_errors is not None and any([error.code == 'required' for error in content_errors]):
                return JsonResponse({
                    "success": False,
                    "message": "Error. Empty input received. Please enter some text to translate."
                })
            elif backend_errors is not None and any([error.code == 'required' for error in backend_errors]):
                return JsonResponse({
                    "success": False,
                    "message": "No backend selected."
                })
            elif form.non_field_errors():
                return JsonResponse({
                    "success": False,
                    "message": "Error. " + "\n".join(form.non_field_errors())
                })
            else:
                logger.warning("Unexpected invalid input." + str(form.errors))
                return JsonResponse({
                    "success": False,
                    "message": "Error in Translation. Contact Organizers."
                })
        text = html.escape(form.cleaned_data["content"])
        input_lang = form.cleaned_data["input_lang"]
        output_lang = form.cleaned_data["output_lang"]
        backend_name = form.cleaned_data["backend"]
        all_backends = backends.get_available_translation_backends()
        if backend_name not in all_backends:
            return JsonResponse({
                "success": False,
                "message": "Invalid Translation Backend. Contact Organizers."
            })
        backend = all_backends[backend_name]

        # Wrap backtick, dollar sign and images in no-translate blocks
        def replacer(match):
            if match.group("image_pattern"):
                # Make sure the description gets translated but not the path
                return (
                    backend.mark_for_notranslate("![") + 
                    f'<span class="translate">{match.group("desc")}</span>' + 
                    backend.mark_for_notranslate(f']({match.group("path")})')
                )
            else:
                # Extract the code block content
                block = match.group(1)
                lines = []
                for line in block.split("\n"):
                    lines.append(backend.mark_for_notranslate(line))
                # Return the code block with spans wrapped around each line
                return "\n".join(lines)
        backtick_pattern = r'(`+)[^`]+?\2'
        dollar_math_pattern = r'(\$+)[^\$]+?\3'
        image_pattern = r'(?P<image_pattern>!\[(?P<desc>[^\n\]]*?)\]\((?P<path>[^\n\)]*?)\))'
        text = re.sub(fr'({backtick_pattern}|{dollar_math_pattern}|{image_pattern})', replacer, text, flags=re.MULTILINE)

        if not hasattr(request.user, "usertranslationquota"):
            UserTranslationQuota.objects.create(
                user=request.user,
                credit=settings.INITIAL_DEFAULT_PER_USER_TRANSLATION_QUOTA)
        updated_rows = (UserTranslationQuota.objects.filter(user=request.user, credit__gte=models.F('used') + len(text))
                        .update(used=models.F('used') + len(text)))
        if updated_rows == 0:
            return JsonResponse({
                "success": False,
                "message": "No Translation Quota. Contact Organizer to Recharge."
            })
        elif updated_rows > 1:
            logging.error("UNEXPECTED PART OF CODE REACHED. THIS SHOULD NOT HAPPEN.")
        try:
            translated_text = backend.translate(text, input_lang, output_lang)
            # Remove no-translate blocks
            translated_text = backend.unmark_for_notranslate(translated_text)
            translated_text = re.sub(r'\s*<span class="translate">(.*?)</span>', r'\1', translated_text, flags=re.MULTILINE)
            translated_text = html.unescape(translated_text)
            new_quota = UserTranslationQuota.objects.get(user=request.user)
            assert new_quota is not None
            return JsonResponse({
                "success": True,
                "message": "",
                "translated_text": translated_text,
                "new_quota": new_quota.credit - new_quota.used,
            })
        except backends.HandledException as e:
            return JsonResponse({
                "success": False,
                "message": str(e),
            })
        except Exception as e:
            logging.error("Error in Translation. ", exc_info=e)
            return JsonResponse({
                "success": False,
                "message": "Error in Translation. Contact Organizers."
            })
