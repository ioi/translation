import datetime

from trans.utils import edit_token


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


def get_requested_user(request, task_type):
    from trans.models import User
    user = User.objects.get(username=request.user)
    if user.is_staff and 'user' in request.GET:
        user = User.objects.get(username=request.GET.get('user'))
    if task_type == 'released':
        user = User.objects.get(username='ISC')
    return user


def get_translate_edit_permission(translation, user_token=None):
    cached_edit_token = edit_token.fetch_cached_edit_token(translation)
    current_time = datetime.datetime.now()

    if cached_edit_token is None:
        new_edit_token = edit_token.EditToken(edit_token.generate_random_token(), datetime.datetime.now())
        edit_token.cache_edit_token(translation, new_edit_token)
        return True, new_edit_token.token

    if user_token == cached_edit_token.token:
        new_edit_token = edit_token.EditToken(user_token, datetime.datetime.now())
        edit_token.cache_edit_token(translation, new_edit_token)
        return True, new_edit_token.token

    # Older token shouldn't be reused once another token has been issued. Frontend can use this information
    # to determine whether another translation editing session has happened.
    if edit_token.is_edit_token_expired(cached_edit_token, current_time):
        new_edit_token = edit_token.EditToken(edit_token.generate_random_token(), datetime.datetime.now())
        edit_token.cache_edit_token(translation, new_edit_token)
        return True, new_edit_token.token

    return False, None


def can_save_translate(translation, user_token):
    cached_edit_token = edit_token.fetch_cached_edit_token(translation)
    if cached_edit_token is None:
        return True

    current_time = datetime.datetime.now()
    return user_token == cached_edit_token.token or edit_token.is_edit_token_expired(cached_edit_token, current_time)


def is_translate_in_editing(translation):
    current_time = datetime.datetime.now()
    cached_edit_token = edit_token.fetch_cached_edit_token(translation)
    if cached_edit_token is None:
        return False
    return not edit_token.is_edit_token_expired(cached_edit_token, current_time)


def unleash_edit_token(translation):
    edit_token.clear_cached_edit_token(translation)
