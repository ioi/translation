from django import template
from django.conf import settings
import pytz
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.utils import timezone

register = template.Library()

@register.filter
def ioi_timezone(value):
    if (type(value) is str):
        value = parse_datetime(value)

    settings_timezone = pytz.timezone(settings.TIME_ZONE)
    now = timezone.now()
    older_one_day = (now - value).total_seconds() > 3600 * 24
    time_format = '%b %d' if older_one_day else '%H:%M'
    title_format = '%B %d, %Y at %H:%M'
    time = value.astimezone(settings_timezone)
    # title = '{} ({})'.format(time.strftime(title_format), settings.TIME_ZONE)
    title = time.strftime(title_format)

    return '<span title="{}">{}</span>'.format(title, time.strftime(time_format))
