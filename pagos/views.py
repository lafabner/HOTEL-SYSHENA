from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView

from core.errores import ErrorNegocio
from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin
from pagos import logica as pl
from reservas.models import Reserva
from servicios import logica as sl
from servicios.models import Servicio

from .models import Pago


class PagosView(RolRequeridoMixin, ListView):
    """UI-09. Cuenta de la reserva, servicios y pagos (CU-12 y CU-13)."""
    roles = ROLES_POR_URL['pagos']
    template_name = 'pagos/pagos.html'
    context_object_name = 'reservas'

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        if accion and pk:
            return self.ejecutar(request, accion, pk)
        return super().get(request, *args, **kwargs)

    def ejecutar(self, request, accion, pk):
        reserva = Reserva.objects.filter(pk=pk).first()
        if reserva is None:
            messages.error(request, 'La reserva no existe.')
            return redirect(reverse('pagos'))
        try:
            if accion == 'servicio':
                servicio = Servicio.objects.filter(
                    pk=request.GET.get('servicio', '')).first()
                cantidad = request.GET.get('cantidad', '1')
                if servicio is None:
                    raise ErrorNegocio('Selecciona un servicio válido.')
                sl.registrar_consumo(reserva, servicio, cantidad, request.user)
                messages.success(request, f'Servicio {servicio.nombre} agregado a {reserva.codigo}.')
            elif accion == 'pago':
                valor = request.GET.get('valor', '')
                metodo = request.GET.get('metodo', Pago.EFECTIVO)
                referencia = request.GET.get('referencia', '')
                pl.registrar_pago(reserva, valor, metodo, request.user, referencia=referencia)
                messages.success(request, f'Abono de ${Decimal(valor):,.0f} registrado.')
            else:
                messages.error(request, 'Acción no permitida.')
        except ErrorNegocio as error:
            messages.error(request, str(error))
        except Exception:
            messages.error(request, 'Verifica el valor o la cantidad.')
        return redirect(reverse('pagos') + f'?reserva={reserva.pk}')

    def get_queryset(self):
        return (Reserva.objects.filter(estado__in=[
                    Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_ESTADIA])
                .select_related('huesped', 'habitacion')
                .order_by('-creado_en', '-id'))

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['pagina_titulo'] = 'Pagos y servicios'
        pk = self.request.GET.get('reserva', '')
        reserva = None
        if pk:
            reserva = Reserva.objects.filter(pk=pk).select_related(
                'huesped', 'habitacion', 'habitacion__tipo_habitacion').first()
        if reserva is None:
            reserva = contexto['reservas'].first() if contexto['reservas'] else None
        contexto['reserva'] = reserva
        if reserva:
            contexto['consumos'] = reserva.consumos.select_related('servicio').order_by('-fecha_hora')
            contexto['pagos'] = reserva.pagos.order_by('-fecha_hora')
            contexto['servicios'] = Servicio.objects.filter(
                alojamiento=reserva.habitacion.alojamiento_id, activo=True)
            contexto['metodos'] = Pago.METODOS
        return contexto
