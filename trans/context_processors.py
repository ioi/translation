from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2022 Task Translation System',
        'CONTEST_TITLE': 'IOI 2022',
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': '/media/images/',
    }}
