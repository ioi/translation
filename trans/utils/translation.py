import datetime
import random
import string

from django.conf import settings
from django.core.cache import cache


def get_trans_edit_cache_key(translation):
    return "TRANS_ET-%d" % translation.id


def get_task_by_contest_and_name(contest_slug, task_name, is_editor=False):
    from trans.models import Contest, Task
    contest = Contest.objects.filter(slug=contest_slug).first()
    if not contest:
        raise Exception("There is no contest")
    task = Task.objects.get(name=task_name, contest=contest)
    if not (is_editor or task.contest.public):
        raise Exception("There is no published task")
    return task


def get_trans_by_user_and_task(user, task):
    from trans.models import Translation
    trans, created = Translation.objects.get_or_create(user=user, task=task)
    if created and task.get_published_text():
        trans.add_version(task.get_published_text())
    return trans


def can_user_change_translation(user, translation, edit_token):
    return user == translation.user and can_save_translate(translation, edit_token) and not translation.frozen


def get_translate_edit_permission(translation, my_token=None):
    if can_save_translate(translation, my_token):
        new_edit_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        cache.set(get_trans_edit_cache_key(translation), (new_edit_key, datetime.datetime.now()))
        return True, new_edit_key
    return False, ""


def can_save_translate(translation, my_token):
    edit_token = cache.get(get_trans_edit_cache_key(translation))
    current_time = datetime.datetime.now()
    return (edit_token is None) or my_token == edit_token[0] or edit_token[1] + datetime.timedelta(
        seconds=settings.TRANSLATION_EDIT_TIME_OUT) < current_time


def is_translate_in_editing(translation):
    current_time = datetime.datetime.now()
    edit_token = cache.get(get_trans_edit_cache_key(translation))
    return (edit_token is not None) and (edit_token[1] + datetime.timedelta(seconds=settings.TRANSLATION_EDIT_TIME_OUT) > current_time)


def unleash_edit_token(translation):
    cache.set(get_trans_edit_cache_key(translation), None)

