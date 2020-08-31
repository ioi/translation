from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2020 Translation Home Page',
        'CONTEST_TITLE': 'IOI 2020',
        'CONTEST_FULL_TITLE': 'International Olympiad in Informatics 2020',
        'CONTEST_DATE': 'September 13\u201319 2020',
        'CONTEST_PLACE': 'Singapore',
        'PRINT_ENABLED': settings.PRINT_SYSTEM_ADDRESS is not None,
        'CUSTOM_PRINT_ENABLED': settings.CUSTOM_PRINT_ENABLED,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}
