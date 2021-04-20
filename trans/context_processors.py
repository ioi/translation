from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2019 Translation Home Page',
        'CONTEST_TITLE': 'IOI 2019',
        'CONTEST_FULL_TITLE': 'International Olympiad in Informatics 2019',
        'CONTEST_DATE': 'August 4\u201311th, 2019',
        'CONTEST_PLACE': 'Baku, Azerbaijan',
        'PRINT_ENABLED': settings.PRINT_ENABLED,
        'CUSTOM_PRINT_ENABLED': settings.CUSTOM_PRINT_ENABLED,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}
