from django import template

register = template.Library()


@register.filter
def format_documento(value):
    if not value:
        return "-"

    value = "".join(filter(str.isdigit, str(value)))

    if len(value) == 11:
        return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:]}"
    
    if len(value) == 14:
        return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:]}"
    
    return value


@register.filter
def format_telefone(value):
    if not value:
        return "-"

    value = "".join(filter(str.isdigit, str(value)))

    if len(value) == 11:
        return f"({value[:2]}) {value[2:7]}-{value[7:]}"
    
    if len(value) == 10:
        return f"({value[:2]}) {value[2:6]}-{value[6:]}"
    
    return value