from django import template

register = template.Library()

@register.filter
def get_dict(d, key):
    return d.get(key) if d else None
