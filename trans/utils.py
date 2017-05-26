import json
import logging
import datetime
import string
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.core.cache import cache
from django.core import serializers

logger = logging.getLogger(__name__)


class AdminCheckMixin(LoginRequiredMixin,object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(AdminCheckMixin, self).dispatch(request, *args, **kwargs)


class StaffCheckMixin(LoginRequiredMixin, object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser or user.groups.filter(name="staff").exists()

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(StaffCheckMixin, self).dispatch(request, *args, **kwargs)


class ISCEditorCheckMixin(LoginRequiredMixin, object):
    user_check_failure_path = 'home'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser or user.groups.filter(name="editor").exists()

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(ISCEditorCheckMixin, self).dispatch(request, *args, **kwargs)


# Task Contest Util


CONTEST_ORDER ={'Day 2': 0, 'Day 1': 1, 'Practice': 2}


def get_task_by_contest_and_title(contest_slug, task_title):
    from trans.models import Contest, Task
    contest = Contest.objects.filter(slug=contest_slug).first()
    if not contest:
        raise Exception("There is no contest")
    task = Task.objects.get(title=task_title, contest=contest)
    if not task.enabled:
        raise Exception("There is no published task")
    return task


def get_trans_by_user_and_task(user, task):
    from trans.models import Translation
    trans, created = Translation.objects.get_or_create(user=user, task=task)
    if created:
        trans.add_version(task.get_published_text())
    return trans


def can_user_change_translation(user, translation, edit_token):
    return user == translation.user and can_save_translate(translation, edit_token) and not translation.freezed

# Cache Utils

def get_user_unread_notifs_cache_key(user):
    return "NOTIF_UN-%d" % user.id


def get_user_read_notifs_cache_key(user):
    return "NOTIF_RN-%d" % user.id


def get_trans_edit_cache_key(translation):
    return "TRANS_ET-%d" % translation.id


# Translation Utils
TRANSLATION_EDIT_TIME_OUT = 120


def get_translate_edit_permission(translation, my_token=None):
    edit_token = cache.get(get_trans_edit_cache_key(translation))
    current_time = datetime.datetime.now()
    if edit_token is None \
            or edit_token[1] + datetime.timedelta(seconds=TRANSLATION_EDIT_TIME_OUT) < current_time \
            or edit_token[0] == my_token:
        new_edit_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        cache.set(get_trans_edit_cache_key(translation), (new_edit_key, current_time))
        return True, new_edit_key
    return False, ""


def can_save_translate(translation, my_token):
    edit_token = cache.get(get_trans_edit_cache_key(translation))
    return (edit_token is None) or my_token == edit_token[0]


def is_translate_in_editing(translation):
    current_time = datetime.datetime.now()
    edit_token = cache.get(get_trans_edit_cache_key(translation))
    return (edit_token is not None) and (edit_token[1] + datetime.timedelta(seconds=TRANSLATION_EDIT_TIME_OUT) > current_time)


def unleash_edit_translation_token(translation):
    cache.set(get_trans_edit_cache_key(translation), None)

# Notifications Util


def update_user_cache(user, all_notifications):
    if cache.get(get_user_read_notifs_cache_key(user)) is None and\
            cache.get(get_user_unread_notifs_cache_key(user)) is None:
        add_all_notifs_to_user_cache(user, all_notifications)


def get_all_notifs(user, all_notifications):
    update_user_cache(user, all_notifications)
    all_notifs = []
    for read_notif in get_all_read_notifs(user):
        read_notif['read'] = True
        all_notifs.append(read_notif)
    for unread_notif in get_all_unread_notifs(user):
        unread_notif['read'] = False
        all_notifs.append(unread_notif)
    return all_notifs


def get_all_unread_notifs(user):
    all_unread_notifs = cache.get(get_user_unread_notifs_cache_key(user))
    return all_unread_notifs if all_unread_notifs else []


def get_all_read_notifs(user):
    all_read_notifs = cache.get(get_user_read_notifs_cache_key(user))
    return all_read_notifs if all_read_notifs else []

def add_all_notifs_to_user_cache(user, notifications):
    all_notif_items = []
    for notif in notifications:
        notif_dict = json.loads(serializers.serialize('json', [notif, ]))[0]
        notif_item = notif_dict['fields']
        notif_item['id'] = notif_dict['pk']
        all_notif_items.append(notif_item)
    unread_notifs = cache.get(get_user_unread_notifs_cache_key(user))
    if unread_notifs is None:
        unread_notifs = []
    unread_notifs += all_notif_items
    cache.set(get_user_unread_notifs_cache_key(user), unread_notifs)

def add_notif_item_to_user_cache(user, notif_item):
    unread_notifs = cache.get(get_user_unread_notifs_cache_key(user))
    if unread_notifs is None:
        unread_notifs = []
    unread_notifs.append(notif_item)
    cache.set(get_user_unread_notifs_cache_key(user), unread_notifs)


def add_notification_to_users_cache(translators, notif):
    notif_dict = json.loads(serializers.serialize('json', [ notif, ]))[0]
    notif_item = notif_dict['fields']
    notif_item['id'] = notif_dict['pk']
    for user in translators:
        add_notif_item_to_user_cache(user, notif_item)


def read_all_notifs(user):
    cache.set(get_user_read_notifs_cache_key(user), get_all_unread_notifs(user) + get_all_read_notifs(user))
    cache.set(get_user_unread_notifs_cache_key(user), [])


def read_this_notif(user, notif):
    all_unread_notifs = get_all_unread_notifs(user)
    remove_notifs = [n for n in all_unread_notifs if n['id'] == notif.id]
    if len(remove_notifs) != 1:
        logger.error('Somethings wrong with this notif %d and this user %d' % (notif.id, user.id))

    cache.set(get_user_read_notifs_cache_key(user), get_all_read_notifs(user) + remove_notifs)
    all_unread_notifs.remove(remove_notifs[0])
    cache.set(get_user_unread_notifs_cache_key(user), all_unread_notifs)