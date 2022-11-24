from django import template


register = template.Library()


@register.filter
def set_format(price):
    return format(price,',')+"원"

@register.filter
def set_size(name):
    return name[0:7] + "..." if len(name) > 7 else name