"""
Custom template tags and filters for performance optimization.
Usage: {% load perf_tags %} then {{ image_url|picture_tag:"alt text" }}
"""
from django import template
from django.utils.safestring import mark_safe
from app.image_utils import generate_picture_tag

register = template.Library()


@register.filter
def picture_tag(image_path, alt_text=''):
    """
    Convert image path to <picture> tag with WebP/AVIF fallback.
    Usage: {{ image.url|picture_tag:"Image description" }}
    """
    if not image_path:
        return ''
    return mark_safe(generate_picture_tag(image_path, alt_text))


@register.filter
def lazy_image(image_path, alt_text=''):
    """
    Simplified lazy-loaded img tag.
    Usage: {{ image.url|lazy_image:"Alt text" }}
    """
    if not image_path:
        return ''
    return mark_safe(f'<img src="{image_path}" alt="{alt_text}" loading="lazy" />')
