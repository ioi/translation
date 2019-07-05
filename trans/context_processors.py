from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2019 Translation',
        'CONTEST_TITLE': 'IOI 2019',
        'CONTEST_FULL_TITLE': 'International Olympiad in Informatics 2019',
        'CONTEST_DATE': 'August 4\u201311th, 2019',
        'CONTEST_PLACE': 'Baku, Azerbaijan',
        'PRINT_ENABLED': settings.PRINT_SYSTEM_ADDRESS is not None,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}
