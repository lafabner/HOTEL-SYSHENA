"""Resolver común para ilustraciones estáticas, sin depender de nombres exactos."""
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.text import slugify

register = template.Library()


@register.filter
def foto_habitacion(nombre):
    nombre = slugify(str(nombre))
    if 'familiar' in nombre:
        tipo = 'familiar'
    elif any(t in nombre for t in ('doble', 'matrimonial', 'suite')):
        tipo = 'doble'
    else:
        tipo = 'sencilla'
    return static(f'img/habitacion-{tipo}.jpg')


@register.filter
def foto_sitio(nombre):
    relativo = f'img/sitios/{slugify(str(nombre))}.jpg'
    if not (Path(settings.BASE_DIR) / 'public' / relativo).is_file():
        relativo = 'img/sitios/paisaje-guajira.jpg'
    return static(relativo)


@register.filter
def moneda_cop(valor):
    try:
        return '$' + f'{Decimal(valor):,.0f}'.replace(',', '.')
    except (InvalidOperation, TypeError, ValueError):
        return 'Consultar'
