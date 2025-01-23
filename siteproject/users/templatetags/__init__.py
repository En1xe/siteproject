from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    """Возвращает только имя файла из полного пути"""
    return os.path.basename(value)