from django.conf import settings


def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI Task Translation System',
        'CONTEST_TITLE': 'IOI',
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
        'ENABLE_AUTO_TRANSLATE': settings.ENABLE_AUTO_TRANSLATE,
    }}


def ioi_user(request):
    user = request.user
    if user is None or not user.is_staff:
        is_editor = False
        is_staff = False
        can_notify = False
    elif user.is_superuser:
        is_editor = True
        is_staff = True
        can_notify = True
    else:
        is_editor = user.groups.filter(name='editor').exists()
        # Beware that this is something different from Django's user.is_staff
        is_staff = user.groups.filter(name='staff').exists()
        can_notify = user.has_perm('trans.send_notifications')

    return {
        'can_send_notifications': can_notify,
        'is_editor': is_editor,
        'is_staff': is_staff,
    }
