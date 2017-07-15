import json
import logging

from django.core.cache import cache
from django.core import serializers
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def get_user_unread_notifs_cache_key(user):
    return "NOTIF_UN-%d" % user.id


def get_user_read_notifs_cache_key(user):
    return "NOTIF_RN-%d" % user.id


def reset_notification_cache(users):
    for user in users:
        cache.set(get_user_unread_notifs_cache_key(user), [])
        cache.set(get_user_read_notifs_cache_key(user), [])


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
    return sorted(all_notifs, key=lambda k: k['create_time'], reverse=True)


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
    unread_notifs.insert(0, notif_item)
    cache.set(get_user_unread_notifs_cache_key(user), unread_notifs)


def add_notification_to_users_cache(users, notif):
    notif_dict = json.loads(serializers.serialize('json', [ notif, ]))[0]
    notif_item = notif_dict['fields']
    notif_item['id'] = notif_dict['pk']
    for user in users:
        add_notif_item_to_user_cache(user, notif_item)


def remove_notification_in_user(user, notif):
    unread_notifs = cache.get(get_user_unread_notifs_cache_key(user))
    if unread_notifs and len(unread_notifs) > 0:
        for un_notif in unread_notifs:
            if un_notif['id'] == notif.id:
                unread_notifs.remove(un_notif)
                cache.set(get_user_unread_notifs_cache_key(user), unread_notifs)
                break
    read_notifs = cache.get(get_user_read_notifs_cache_key(user))
    if read_notifs and len(read_notifs) > 0:
        for read_notif in read_notifs:
            if read_notif['id'] == notif.id:
                read_notifs.remove(read_notif)
                cache.set(get_user_read_notifs_cache_key(user), read_notifs)
                break


def remove_notification(users, notif):
    for user in users:
        remove_notification_in_user(user, notif)


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
