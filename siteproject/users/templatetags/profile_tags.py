from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    """Возвращает только имя файла из полного пути"""
    if hasattr(value, 'name'):
        return os.path.basename(value.name)
    return value