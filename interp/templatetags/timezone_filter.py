from django import template
import pytz

register = template.Library()

@register.filter
def ioi_timezone(value):
    tehran = pytz.timezone('Asia/Tehran')
    fmt = '%b %d, %H:%M %Z'

    return value.astimezone(tehran).strftime(fmt)