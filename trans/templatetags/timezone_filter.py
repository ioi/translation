from django import template
from django.conf import settings
import pytz
from django.utils.dateparse import parse_datetime


register = template.Library()

@register.filter
def ioi_timezone(value):
    if(type(value) is str):
        value = parse_datetime(value)

    settings_timezone = pytz.timezone(settings.TIME_ZONE)
    fmt = '%b %d, %H:%M'

    return value.astimezone(settings_timezone).strftime(fmt)
