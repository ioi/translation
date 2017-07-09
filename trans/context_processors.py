
def ioi_settings(request):
    settings = {
        'SITE_TITLE': 'IOI 2017 Translation',
        'CONTEST_TITLE': 'IOI 2017',
        'PRINT_ENABLED': True,
        'IMAGES_URL': '/media/uploads/'
    }
    return {'settings': settings}
