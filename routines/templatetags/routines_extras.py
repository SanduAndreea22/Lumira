from django import template

register = template.Library()


@register.filter
def dict_get(mapping, key):
    return mapping.get(str(key))


_CATEGORY_ICONS = {
    "cleanser": "droplet",
    "serum": "sparkle",
    "moisturizer": "leaf",
    "spf": "shield",
    "treatment": "target",
    "night_cream": "clock",
    "exfoliant": "leaf",
}


@register.filter
def category_icon(category):
    return _CATEGORY_ICONS.get(category, "sparkle")
