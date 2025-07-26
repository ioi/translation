from django.conf import settings

from autotranslate import backends

_cached_language_list = None

__all__ = ["get_supported_languages"]

def get_available_translation_backend_names() -> list[str]:
    return list(backends.get_available_translation_backends().keys())

def get_supported_languages():
    if not settings.ENABLE_AUTO_TRANSLATE:
        return []
    global _cached_language_list
    if _cached_language_list is None:
        # TODO: This will not work with deployment as they will fork before this function is called.
        # TODO: Find a better way to handle this
        _cached_language_list = {}
        for backend_name, backend in backends.get_available_translation_backends().items():
            backend_langs = backend.get_supported_languages()
            for lang_code, lang_name in backend_langs:
                if lang_code.lower() in _cached_language_list:
                    assert lang_name.lower() == _cached_language_list[lang_code.lower()].lower(), (lang_code, lang_name, _cached_language_list[lang_code.lower()])
                else:
                    _cached_language_list[lang_code.lower()] = lang_name
        _cached_language_list = list(_cached_language_list.items())
    return _cached_language_list