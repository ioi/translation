from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': f"{settings.CONTEST_TITLE} Translation",
        'SITE_AUTHOR': f"{settings.CONTEST_TITLE} HTC",
        'CONTEST_TITLE': settings.CONTEST_TITLE,
        'CONTEST_FULL_TITLE': settings.CONTEST_FULL_TITLE,
        'CONTEST_DATE': settings.CONTEST_DATE,
        'CONTEST_PLACE': settings.CONTEST_PLACE,
        'PRINT_ENABLED': settings.PRINT_SYSTEM_ADDRESS is not None,
        'CUSTOM_PRINT_ENABLED': settings.CUSTOM_PRINT_ENABLED,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}

