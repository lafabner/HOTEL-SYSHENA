from django.db import transaction
from django.utils import timezone

from core.errores import ErrorNegocio
from habitaciones.models import Habitacion

from .models import Reserva, SolicitudCancelacion

MODIFICABLES = (Reserva.PENDIENTE, Reserva.CONFIRMADA)


def validar_fechas(entrada, salida, permitir_pasado=False):
    if not entrada or not salida:
        raise ErrorNegocio('Debe indicar las fechas de entrada y salida.')
    if salida <= entrada:
        raise ErrorNegocio('La fecha de salida debe ser posterior a la fecha de entrada.')
    if not permitir_pasado and entrada < timezone.localdate():
        raise ErrorNegocio('La fecha de entrada no puede estar en el pasado.')


def reservas_que_cruzan(habitacion, entrada, salida, excluir=None):
    qs = Reserva.objects.filter(
        habitacion=habitacion,
        estado__in=Reserva.ESTADOS_BLOQUEANTES,
        fecha_entrada__lt=salida,
        fecha_salida__gt=entrada,
    )
    if excluir is not None:
        qs = qs.exclude(pk=excluir.pk)
    return qs


def habitaciones_disponibles(entrada, salida, huespedes, alojamiento=None, tipo=None):
    validar_fechas(entrada, salida)
    if not huespedes or huespedes < 1:
        raise ErrorNegocio('El número de huéspedes debe ser mayor que cero.')
    ocupadas = Reserva.objects.filter(
        estado__in=Reserva.ESTADOS_BLOQUEANTES,
        fecha_entrada__lt=salida,
        fecha_salida__gt=entrada,
    ).values('habitacion_id')
    qs = (Habitacion.objects.filter(activa=True, capacidad__gte=huespedes)
          .exclude(pk__in=ocupadas).select_related('tipo_habitacion'))
    if alojamiento is not None:
        qs = qs.filter(alojamiento=alojamiento)
    if tipo is not None:
        qs = qs.filter(tipo_habitacion=tipo)
    return qs.order_by('precio_noche', 'numero')


@transaction.atomic
def crear_reserva(*, huesped, habitacion, fecha_entrada, fecha_salida, numero_huespedes,
                  creada_por, observaciones='', estado=Reserva.PENDIENTE,
                  permitir_pasado=False):
    validar_fechas(fecha_entrada, fecha_salida, permitir_pasado)
    habitacion = Habitacion.objects.select_for_update().get(pk=habitacion.pk)
    if not habitacion.activa:
        raise ErrorNegocio('La habitación no está activa.')
    if not numero_huespedes or numero_huespedes < 1:
        raise ErrorNegocio('El número de huéspedes debe ser mayor que cero.')
    if numero_huespedes > habitacion.capacidad:
        raise ErrorNegocio(f'La habitación {habitacion.numero} admite máximo '
                           f'{habitacion.capacidad} huésped(es).')
    if reservas_que_cruzan(habitacion, fecha_entrada, fecha_salida).exists():
        raise ErrorNegocio(f'La habitación {habitacion.numero} ya está reservada en esas fechas.')
    reserva = Reserva(
        huesped=huesped, habitacion=habitacion, creada_por=creada_por,
        fecha_entrada=fecha_entrada, fecha_salida=fecha_salida,
        numero_huespedes=numero_huespedes, estado=estado,
        tarifa_noche=habitacion.precio_noche, observaciones=observaciones or None,
    )
    reserva.save()
    return reserva


@transaction.atomic
def confirmar_reserva(reserva):
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado != Reserva.PENDIENTE:
        raise ErrorNegocio('Solo se pueden confirmar reservas pendientes.')
    reserva.estado = Reserva.CONFIRMADA
    reserva.save(update_fields=['estado', 'actualizado_en'])
    return reserva


@transaction.atomic
def cancelar_reserva(reserva, motivo, usuario):
    """CU-09 (flujo administrativo): cancela y conserva el historial."""
    if not motivo or not motivo.strip():
        raise ErrorNegocio('Debe registrar el motivo de la cancelación.')
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado not in MODIFICABLES:
        raise ErrorNegocio(f'No se puede cancelar una reserva en estado {reserva.get_estado_display()}.')
    reserva.estado = Reserva.CANCELADA
    nota = f'[Cancelada por {usuario}] {motivo.strip()}'
    reserva.observaciones = f'{reserva.observaciones}\n{nota}' if reserva.observaciones else nota
    reserva.save(update_fields=['estado', 'observaciones', 'actualizado_en'])
    reserva.solicitudes_cancelacion.filter(estado=SolicitudCancelacion.PENDIENTE).update(
        estado=SolicitudCancelacion.APROBADA, resuelta_por=usuario,
        fecha_resolucion=timezone.now(), respuesta='Reserva cancelada por el personal.')
    return reserva
