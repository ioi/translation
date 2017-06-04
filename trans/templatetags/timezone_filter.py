from django import template
from django.conf import settings
import pytz

register = template.Library()

@register.filter
def ioi_timezone(value):
    settings_timezone = pytz.timezone(settings.TIME_ZONE)
    fmt = '%b %d @ %H:%M'

    return value.astimezone(settings_timezone).strftime(fmt)
