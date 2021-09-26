from collections import namedtuple
import datetime
import random
import string

from django.core.cache import cache
from django.conf import settings


EditToken = namedtuple('EditToken', ['token', 'created_datetime'])


def _trans_edit_cache_key(translation):
    return 'TRANS_ET-%d' % translation.id


def fetch_cached_edit_token(translation):
    return cache.get(_trans_edit_cache_key(translation))


def clear_cached_edit_token(translation):
    cache.set(_trans_edit_cache_key(translation), None)


def cache_edit_token(translation, edit_token):
    if not isinstance(edit_token, EditToken):
        raise TypeError('New edit_token must be an instance of EditToken')
    cache.set(_trans_edit_cache_key(translation), edit_token)


def is_edit_token_expired(edit_token, current_time):
    return edit_token.created_datetime + datetime.timedelta(seconds=settings.TRANSLATION_EDIT_TIME_OUT) < current_time


def generate_random_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

