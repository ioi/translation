import dataclasses
import deepl
import html
import re

from google.cloud import translate as gcloud_translate

from django.conf import settings


@dataclasses.dataclass(frozen=True)
class TranslationBackend:
    name: str

    def is_available(self) -> bool:
        ...

    def translate(self, text: str, input_lang: str, output_lang: str) -> str:
        ...

    def mark_for_notranslate(self, text: str) -> str:
        ...

    def unmark_for_notranslate(self, text: str) -> str:
        ...

    def get_supported_languages(self) -> list[tuple[str, str]]:
        ...

class HandledException(Exception):
    pass

@dataclasses.dataclass(frozen=True)
class GoogleCloudTranslate(TranslationBackend):
    name: str = 'Google Translate'

    def is_available(self):
        return settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH is not None

    def get_supported_languages(self):
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
        client = gcloud_translate.TranslationServiceClient.from_service_account_file(
            settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
        response = client.get_supported_languages(display_language_code="en", parent=parent)
        return [(lang.language_code, lang.display_name) for lang in response.languages]

    def translate(self, text: str, input_lang: str, output_lang: str):
        client = gcloud_translate.TranslationServiceClient.from_service_account_file(
            settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
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
        
        translated_text_match = re.fullmatch(r"<pre.*?>(.*)</pre>", translated_text, re.DOTALL)
        assert translated_text_match is not None, translated_text
        translated_text = translated_text_match.group(1)
        
        return translated_text

    def mark_for_notranslate(self, text):
        return f'<span class="notranslate">{text}</span>'

    def unmark_for_notranslate(self, text):
        text = re.sub(
            r'</span>\s*<span class="notranslate">(.*?)</span>', 
            r'</span>\1', text, flags=re.MULTILINE)
        return re.sub(
            r'<span class="notranslate">(.*?)</span>', 
            r'\1', text, flags=re.MULTILINE)


@dataclasses.dataclass(frozen=True)
class DeepLTranslate(TranslationBackend):
    name: str = "DeepL"

    def is_available(self):
        return settings.DEEPL_API_KEY is not None

    def get_supported_languages(self):
        client = deepl.DeepLClient(settings.DEEPL_API_KEY)
        status, content, json = client._api_call("/v2/languages?type=target")
        client._raise_for_status(status, content, json)
        return [(lang["language"], lang["name"]) for lang in json]

    def translate(self, text: str, input_lang: str, output_lang: str):
        client = deepl.DeepLClient(settings.DEEPL_API_KEY)
        try:
            response = client.translate_text(
                "<pre>" + text + "</pre>",
                **{
                    "tag_handling": "xml", 
                    "preserve_formatting": True,
                    "source_lang": input_lang,
                    "target_lang": output_lang,
                    "ignore_tags": ["notranslate"]
                }
            )
        except deepl.exceptions.DeepLException as e:
            message = str(e)
            if "message: Value for 'target_lang' not supported." in message:
                raise HandledException("Target language is not supported by this backend.")
            elif "message: Value for 'source_lang' not supported." in message:
                raise HandledException("Source language is not supported by this backend.")
            else:
                raise e
        translated_text = response.text
        translated_text_match = re.fullmatch(r"<pre.*?>(.*)</pre>", translated_text, re.DOTALL)
        assert translated_text_match is not None, translated_text
        translated_text = translated_text_match.group(1)
        
        return translated_text

    def mark_for_notranslate(self, text):
        return f'<notranslate>{text}</notranslate>'

    def unmark_for_notranslate(self, text):
        return re.sub(
            r'<notranslate>(.*?)</notranslate>', 
            r'\1', text, flags=re.MULTILINE)



def get_available_translation_backends() -> dict[str, TranslationBackend]:
    all_backends = [
        GoogleCloudTranslate(),
        DeepLTranslate(),
    ]
    return {
        backend.name: backend 
        for backend in all_backends 
        if backend.is_available()
    }