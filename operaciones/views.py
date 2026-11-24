from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from core.errores import ErrorNegocio
from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin
from reservas.models import Reserva

from . import logica as ol
from .models import Estadia


class OperacionView(RolRequeridoMixin, ListView):
    """UI-08. Llegadas, estadías en curso y salidas (CU-11 y CU-14)."""
    roles = ROLES_POR_URL['operacion']
    template_name = 'operaciones/operacion.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        hoy = timezone.localdate()
        return (Reserva.objects.filter(fecha_salida__gte=hoy)
               .select_related('huesped', 'habitacion', 'habitacion__tipo_habitacion')
               .order_by('fecha_entrada', 'id'))

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        if accion and pk:
            return self.ejecutar(request, accion, pk)
        return super().get(request, *args, **kwargs)

    def ejecutar(self, request, accion, pk):
        reserva = Reserva.objects.filter(pk=pk).select_related('habitacion').first()
        if reserva is None:
            messages.error(request, 'La reserva no existe.')
            return redirect(reverse('operacion'))
        try:
            if accion == 'checkin':
                ol.realizar_checkin(reserva, request.user, request.GET.get('obs', ''))
                messages.success(request, f'Check-in de {reserva.codigo} registrado.')
            elif accion == 'checkout':
                ol.realizar_checkout(reserva, request.user, request.GET.get('obs', ''))
                messages.success(request, f'Check-out de {reserva.codigo} registrado.')
            else:
                messages.error(request, 'Acción no permitida.')
        except ErrorNegocio as error:
            messages.error(request, str(error))
        return redirect(reverse('operacion'))

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        hoy = timezone.localdate()
        reservas = contexto['reservas']
        en_curso_ids = set(Estadia.objects.filter(fecha_hora_checkout__isnull=True)
                           .values_list('reserva_id', flat=True))
        contexto['pagina_titulo'] = 'Check-in y Check-out'
        contexto['llegadas_hoy'] = [r for r in reservas
                                    if r.fecha_entrada == hoy and r.estado in
                                    (Reserva.PENDIENTE, Reserva.CONFIRMADA)]
        contexto['en_curso'] = [r for r in reservas
                                if r.pk in en_curso_ids and r.estado == Reserva.EN_ESTADIA]
        contexto['salidas_hoy'] = [r for r in reservas
                                   if r.fecha_salida == hoy and r.estado == Reserva.EN_ESTADIA]
        contexto['total'] = reservas.count()
        return contexto
