from django.conf import settings


def site_font(request):
    """Context processor that exposes SITE_FONT_FAMILY to all templates.

    The value should be a valid CSS font-family string, for example:
    "'Times New Roman', Times, serif"
    """
    return {
        'SITE_FONT_FAMILY': getattr(settings, 'SITE_FONT_FAMILY', "'Times New Roman', Times, serif"),
    }
