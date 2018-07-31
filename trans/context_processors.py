from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2018 Translation',
        'CONTEST_TITLE': 'IOI 2018',
        'CONTEST_FULL_TITLE': 'International Olympiad in Informatics 2018',
        'CONTEST_DATE': 'September 2\u20137th, 2018',
        'CONTEST_PLACE': 'Tsukuba, Japan',
        'PRINT_ENABLED': settings.PRINT_SYSTEM_ADDRESS is not None,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': settings.HOST_URL + 'media/images/',
        'HOST_URL': settings.HOST_URL
    }}
