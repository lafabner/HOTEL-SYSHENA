from decimal import Decimal, InvalidOperation

from django.db import transaction

from core.errores import ErrorNegocio
from reservas.models import Reserva

from .models import Pago


@transaction.atomic
def registrar_pago(reserva, valor, metodo, usuario, referencia='', observacion=''):
    """CU-13: valor positivo, no mayor al saldo, y recalcula la reserva."""
    try:
        valor = Decimal(str(valor))
    except InvalidOperation:
        raise ErrorNegocio('El valor del pago no es válido.')
    if valor <= 0:
        raise ErrorNegocio('El valor del pago debe ser mayor que cero.')
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado == Reserva.CANCELADA:
        raise ErrorNegocio('No se pueden registrar pagos en una reserva cancelada.')
    if valor > reserva.saldo_pendiente:
        raise ErrorNegocio(f'El valor (${valor:,.0f}) supera el saldo pendiente '
                           f'(${reserva.saldo_pendiente:,.0f}).')
    return Pago.objects.create(
        reserva=reserva, registrado_por=usuario, valor=valor, metodo=metodo,
        referencia=referencia or None, observacion=observacion or None)
