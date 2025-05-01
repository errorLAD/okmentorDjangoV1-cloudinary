from django import template

register = template.Library()

@register.filter
def split_by_comma(value):
    """Splits a string by comma and trims whitespace."""
    if not value:
        return []
    return [v.strip() for v in value.split(',')]
