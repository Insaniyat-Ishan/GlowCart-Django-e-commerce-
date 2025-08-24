# catalog/templatetags/shop_extras.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def money(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return value


@register.simple_tag(takes_context=True)
def qs_replace(context, **kwargs):
    """Return current querystring with some keys replaced/removed."""
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v in (None, "", False):
            query.pop(k, None)
        else:
            query[k] = v
    s = query.urlencode()
    return f"?{s}" if s else "?"


@register.simple_tag
def stars(avg):
    """Return 0–5 stars with halves using Bootstrap Icons."""
    try:
        avg = float(avg or 0)
    except Exception:
        avg = 0.0
    full = int(avg)
    half = 1 if (avg - full) >= 0.5 else 0
    empty = 5 - full - half
    html = '<span class="text-warning">' \
           + ('<i class="bi bi-star-fill"></i>' * full) \
           + ('<i class="bi bi-star-half"></i>' if half else '') \
           + ('<i class="bi bi-star"></i>' * empty) \
           + '</span>'
    return mark_safe(html)
