from django import template

register = template.Library()


@register.filter
def split(value, delimiter=','):
    """
    Split a string by delimiter and return a list.
    Usage: {{ skills|split:"," }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter)]


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    Usage: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
