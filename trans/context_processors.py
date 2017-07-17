from django.conf import settings

def ioi_settings(request):
    return {'settings': {
        'SITE_TITLE': 'IOI 2017 Translation',
        'CONTEST_TITLE': 'IOI 2017',
        'PRINT_ENABLED': True,
        'TIME_ZONE': settings.TIME_ZONE,
        'IMAGES_URL': request.scheme + '://' + request.get_host() + '/media/images/'
    }}
