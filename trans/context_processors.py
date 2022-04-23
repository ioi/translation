from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2022 Translation System',
        'CONTEST_TITLE': 'IOI 2022',
        'CONTEST_FULL_TITLE': 'International Olympiad in Informatics 2022',
        'CONTEST_DATE': 'August 7\u201315th, 2022',
        'CONTEST_PLACE': 'Yogyakarta, Indonesia',
        'PRINT_ENABLED': settings.PRINT_ENABLED,
        'CUSTOM_PRINT_ENABLED': settings.CUSTOM_PRINT_ENABLED,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}
