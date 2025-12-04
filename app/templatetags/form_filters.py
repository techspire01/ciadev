
from django import template
register = template.Library()

# Add errors filter for dynamic form field error access
@register.filter
def errors(field):
    """
    Return errors for a form field, or empty list if not present.
    Usage: {{ field|errors }}
    """
    try:
        return field.errors
    except Exception:
        return []

# Add get_field filter for dynamic form field access
@register.filter
def get_field(form, name):
    """
    Get a form field by dynamic name, e.g. {{ form|get_field:'product1' }}
    """
    try:
        return form[name]
    except Exception:
        return ''

def get(mapping, key):
    """
    Return mapping[key] for forms/dict-like objects.
    Safe: returns empty string if lookup fails.
    Usage in template: {{ form|get:field_name }}
    """
    try:
        return mapping[key]
    except Exception:
        # fallback for dict-like objects with .get
        try:
            return mapping.get(key, '')
        except Exception:
            return ''

@register.filter
def has_key(mapping, key):
    """
    Return True if key in mapping.
    Usage in template: {% if mapping|has_key:key %} ...
    """
    try:
        return key in mapping
    except Exception:
        return False

@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field widget.
    Usage: {{ form.field|add_class:"form-input w-full" }}
    """
    if hasattr(field, 'as_widget'):
        # For form fields
        return field.as_widget(attrs={'class': css_class})
    else:
        # For other objects, return as is
        return field

# Register this Library with the Django template engine's builtins so templates
# don't need an explicit {% load form_filters %}. This uses the public engines API.
try:
    from django.template import engines
    django_engine = engines['django']
    # template_builtins is a list of Library objects; append if not present
    if register not in getattr(django_engine.engine, 'template_builtins', []):
        django_engine.engine.template_builtins.append(register)
except Exception:
    # If anything goes wrong, fail silently — templates can still use {% load form_filters %}
    pass
