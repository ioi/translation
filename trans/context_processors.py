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
    if user is None:
        is_editor = False
    else:
        is_editor = user.is_staff and user.groups.filter(name='editor').exists() or user.is_superuser

    return {
        'is_editor': is_editor,
    }
