from django.conf import settings

from autotranslate import backends

_cached_backend_languages = None

__all__ = ["get_supported_languages"]

def get_available_translation_backend_names() -> list[str]:
    return list(backends.get_available_translation_backends().keys())


def get_supported_languages_per_backend():
    if not settings.ENABLE_AUTO_TRANSLATE:
        return {}
    global _cached_backend_languages
    if _cached_backend_languages is None:
        # TODO: This will not work with deployment as they will fork before this function is called.
        # TODO: Find a better way to handle this
        _cached_backend_languages = {}
        for backend_name, backend in backends.get_available_translation_backends().items():
            # get_supported_languages returns list of (lang_code, lang_name)
            langs = []
            for lang_code, lang_name in backend.get_supported_languages():
                if lang_code.lower() in ['en-us', 'en_us']:
                    lang_code = 'en'
                    lang_name = 'English'
                langs.append((lang_code.lower(), lang_name))
            _cached_backend_languages[backend_name] = langs
    return _cached_backend_languages


def get_supported_languages():
    if not settings.ENABLE_AUTO_TRANSLATE:
        return []
    language_list = {}
    for backend_name, backend_langs in get_supported_languages_per_backend().items():
        for lang_code, lang_name in backend_langs:
            if lang_code.lower() in language_list:
                assert lang_name.lower() == language_list[lang_code.lower()].lower(), (lang_code, lang_name, language_list[lang_code.lower()])
            else:
                language_list[lang_code.lower()] = lang_name
    language_list = list(language_list.items())
    return language_list

