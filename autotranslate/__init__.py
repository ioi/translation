from django.conf import settings
from google.cloud import translate

_cached_language_list = None

__all__ = ["get_supported_languages"]

def get_supported_languages():
    global _cached_language_list
    if _cached_language_list is None:
        # TODO: This will not work with deployment as they will fork before this function is called.
        # TODO: Find a better way to handle this
        client = translate.TranslationServiceClient.from_service_account_file(settings.GCLOUD_SERVICE_ACCOUNT_JSON_PATH)
        location = "global"
        parent = f"projects/{settings.GCLOUD_PROJECT_ID}/locations/{location}"
        response = client.get_supported_languages(display_language_code="en", parent=parent)
        _cached_language_list = [(lang.language_code, lang.display_name) for lang in response.languages]
    return _cached_language_list