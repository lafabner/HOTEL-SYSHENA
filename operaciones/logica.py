from django.db import transaction
from django.utils import timezone

from core.errores import ErrorNegocio
from habitaciones.models import Habitacion
from reservas.models import Reserva

from .models import Estadia


@transaction.atomic
def realizar_checkin(reserva, usuario, observaciones=''):
    """CU-11: crea la estadía, reserva -> EN_ESTADIA, habitación -> OCUPADA."""
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado not in (Reserva.PENDIENTE, Reserva.CONFIRMADA):
        raise ErrorNegocio(f'No se puede hacer check-in a una reserva en estado {reserva.get_estado_display()}.')
    if Estadia.objects.filter(reserva=reserva).exists():
        raise ErrorNegocio('Esta reserva ya tiene check-in registrado.')
    habitacion = Habitacion.objects.select_for_update().get(pk=reserva.habitacion_id)
    if not habitacion.activa or habitacion.estado != Habitacion.DISPONIBLE:
        raise ErrorNegocio(f'La habitación {habitacion.numero} no está disponible '
                           f'(estado: {habitacion.get_estado_display()}).')
    estadia = Estadia.objects.create(
        reserva=reserva, usuario_checkin=usuario, fecha_hora_checkin=timezone.now(),
        observaciones_checkin=observaciones or None)
    reserva.estado = Reserva.EN_ESTADIA
    reserva.save(update_fields=['estado', 'actualizado_en'])
    habitacion.estado = Habitacion.OCUPADA
    habitacion.save(update_fields=['estado'])
    return estadia


@transaction.atomic
def realizar_checkout(reserva, usuario, observaciones=''):
    """CU-14: exige check-in y saldo en cero; libera la habitación."""
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado != Reserva.EN_ESTADIA:
        raise ErrorNegocio('Solo se puede hacer check-out a una reserva con check-in.')
    estadia = Estadia.objects.select_for_update().filter(reserva=reserva).first()
    if estadia is None or estadia.fecha_hora_checkout is not None:
        raise ErrorNegocio('La reserva no tiene una estadía abierta.')
    reserva.recalcular_totales()
    if reserva.saldo_pendiente != 0:
        raise ErrorNegocio(f'La reserva tiene un saldo pendiente de ${reserva.saldo_pendiente:,.0f}. '
                           'Complete el pago antes del check-out.')
    estadia.usuario_checkout = usuario
    estadia.fecha_hora_checkout = timezone.now()
    estadia.observaciones_checkout = observaciones or None
    estadia.save()
    reserva.estado = Reserva.FINALIZADA
    reserva.save(update_fields=['estado', 'actualizado_en'])
    habitacion = Habitacion.objects.select_for_update().get(pk=reserva.habitacion_id)
    habitacion.estado = Habitacion.DISPONIBLE
    habitacion.save(update_fields=['estado'])
    return estadia
