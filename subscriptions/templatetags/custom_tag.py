from django import template


register = template.Library()


@register.filter
def set_format(price):
    return format(price,',')+"원"

@register.filter
def set_size(name, args):
    _params = args.split(',')
    num = int(_params[0])
    _bool = _params[1]
    if _bool == "T":
        return name[0:num] + "..." if len(name) > num else name
    elif _bool == "F":
        return name[0:num] if len(name) > num else name