from django.db import transaction

from core.errores import ErrorNegocio
from reservas.models import Reserva

from .models import ServicioReserva


@transaction.atomic
def registrar_consumo(reserva, servicio, cantidad, usuario):
    """CU-12: conserva el precio unitario vigente y recalcula la cuenta."""
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado in (Reserva.CANCELADA, Reserva.FINALIZADA):
        raise ErrorNegocio(f'No se pueden registrar consumos en una reserva '
                            f'{reserva.get_estado_display().lower()}.')
    if not servicio.activo:
        raise ErrorNegocio('El servicio no está activo.')
    if servicio.alojamiento_id != reserva.habitacion.alojamiento_id:
        raise ErrorNegocio('El servicio no pertenece al alojamiento de la reserva.')
    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ErrorNegocio('La cantidad debe ser un número entero.')
    if cantidad < 1:
        raise ErrorNegocio('La cantidad debe ser mayor que cero.')
    return ServicioReserva.objects.create(
        reserva=reserva, servicio=servicio, cantidad=cantidad,
        precio_unitario=servicio.precio, registrado_por=usuario)
