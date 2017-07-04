from django.conf import settings

def ioi_settings(request):
    imported_settings = ['SITE_TITLE', 'CONTEST_TITLE', 'PRINT_ENABLED']
    data = {i: getattr(settings, i) for i in imported_settings}
    return {'settings': data}
