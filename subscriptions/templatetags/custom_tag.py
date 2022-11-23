from django import template


register = template.Library()


@register.filter
def set_format(price):
    return format(price,',')+"원"