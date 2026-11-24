from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, ListView

from core.errores import ErrorNegocio
from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin
from huespedes.models import Huesped

from . import logica as rl
from .forms import EstadiaForm, HuespedReservaForm
from .models import Reserva, SolicitudCancelacion

class ReservasView(RolRequeridoMixin, ListView):
    """UI-05. Lista y gestiona el ciclo de las reservas (CU-08 y CU-09)."""
    roles = ROLES_POR_URL['reservas']
    template_name = 'reservas/reservas.html'
    context_object_name = 'reservas'
    paginate_by = 20

    def get_queryset(self):
        qs = (Reserva.objects.select_related('huesped', 'habitacion', 'habitacion__tipo_habitacion')
              .order_by('-creado_en', '-id'))
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(codigo__icontains=q)
                | Q(huesped__nombres__icontains=q)
                | Q(huesped__apellidos__icontains=q)
                | Q(huesped__numero_documento__icontains=q))
        estado = self.request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)
        desde = self.request.GET.get('desde', '')
        if desde:
            qs = qs.filter(fecha_entrada__gte=desde)
        habitacion = self.request.GET.get('habitacion', '')
        if habitacion:
            qs = qs.filter(habitacion__numero=habitacion)
        return qs

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        if accion and pk:
            if accion in ('aprobar_solicitud', 'rechazar_solicitud'):
                return self.ejecutar_solicitud(request, accion, pk)
            return self.ejecutar_accion(request, accion, pk)
        return super().get(request, *args, **kwargs)

    def ejecutar_accion(self, request, accion, pk):
        """Confirma o cancela desde la tabla. Si algo falla, vuelve a la lista."""
        reserva = Reserva.objects.filter(pk=pk).first()
        if reserva is None:
            messages.error(request, 'La reserva no existe.')
            return redirect(reverse('reservas'))
        try:
            if accion == 'confirmar':
                rl.confirmar_reserva(reserva)
                messages.success(request, f'Reserva {reserva.codigo} confirmada.')
            elif accion == 'cancelar':
                motivo = request.GET.get('motivo', '').strip()
                if not motivo:
                    messages.error(request, 'Debes escribir el motivo para cancelar.')
                    return redirect(reverse('reservas'))
                rl.cancelar_reserva(reserva, motivo, request.user)
                messages.success(request, f'Reserva {reserva.codigo} cancelada.')
            else:
                messages.error(request, 'Acción no permitida.')
        except ErrorNegocio as error:
            messages.error(request, str(error))
        return redirect(reverse('reservas'))

    def ejecutar_solicitud(self, request, accion, pk):
        """Aprueba o rechaza una solicitud de cancelación del cliente."""
        solicitud = (SolicitudCancelacion.objects
                     .filter(pk=pk, estado=SolicitudCancelacion.PENDIENTE)
                     .select_related('reserva').first())
        if solicitud is None:
            messages.error(request, 'La solicitud no existe o ya fue resuelta.')
            return redirect(reverse('reservas'))
        try:
            if accion == 'aprobar_solicitud':
                rl.cancelar_reserva(solicitud.reserva, solicitud.motivo, request.user)
                messages.success(request, f'Solicitud aprobada: la reserva '
                                          f'{solicitud.reserva.codigo} quedó cancelada.')
            elif accion == 'rechazar_solicitud':
                respuesta = request.GET.get('respuesta', '').strip()
                if not respuesta:
                    messages.error(request, 'Debes escribir la respuesta para el cliente.')
                    return redirect(reverse('reservas'))
                solicitud.estado = SolicitudCancelacion.RECHAZADA
                solicitud.resuelta_por = request.user
                solicitud.fecha_resolucion = timezone.now()
                solicitud.respuesta = respuesta
                solicitud.save()
                messages.success(request, f'Solicitud de {solicitud.reserva.codigo} rechazada.')
            else:
                messages.error(request, 'Acción no permitida.')
        except ErrorNegocio as error:
            messages.error(request, str(error))
        return redirect(reverse('reservas'))

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['pagina_titulo'] = 'Reservas'
        contexto['estados'] = Reserva.ESTADOS
        contexto['estado_actual'] = self.request.GET.get('estado', '')
        contexto['q_actual'] = self.request.GET.get('q', '')
        contexto['desde_actual'] = self.request.GET.get('desde', '')
        contexto['habitacion_actual'] = self.request.GET.get('habitacion', '')
        contexto['puede_cancelar'] = True
        contexto['solicitudes'] = (SolicitudCancelacion.objects
                                   .filter(estado=SolicitudCancelacion.PENDIENTE)
                                   .select_related('reserva', 'reserva__huesped',
                                                   'solicitada_por')[:10])
        return contexto


class NuevaReservaView(RolRequeridoMixin, TemplateView):
    """UI-04. Crea una reserva con validación completa (CU-07)."""
    roles = ROLES_POR_URL['nueva_reserva']
    template_name = 'reservas/nueva_reserva.html'

    def get(self, request, *args, **kwargs):
        huesped_actual = getattr(request.user, 'huesped', None)
        inicial = {
            'fecha_entrada': request.GET.get('entrada', ''),
            'fecha_salida': request.GET.get('salida', ''),
            'numero_huespedes': request.GET.get('huespedes', 1),
            'observaciones': '',
        }
        if huesped_actual:
            huesped_form = HuespedReservaForm(instance=huesped_actual,
                                              huesped_actual=huesped_actual)
        else:
            huesped_form = HuespedReservaForm()
        estadia_form = EstadiaForm(initial=inicial, usuario=request.user)
        habitacion_id = request.GET.get('habitacion')
        if habitacion_id:
            estadia_form.initial['habitacion'] = habitacion_id
        return self.render(request, huesped_form, estadia_form)

    def post(self, request, *args, **kwargs):
        huesped_actual = getattr(request.user, 'huesped', None)
        huesped_form = HuespedReservaForm(request.POST, instance=huesped_actual,
                                         huesped_actual=huesped_actual)
        estadia_form = EstadiaForm(request.POST, usuario=request.user)
        if huesped_form.is_valid() and estadia_form.is_valid():
            try:
                huesped = huesped_actual or huesped_form.save()
                d = estadia_form.cleaned_data
                reserva = rl.crear_reserva(
                    huesped=huesped, habitacion=d['habitacion'],
                    fecha_entrada=d['fecha_entrada'], fecha_salida=d['fecha_salida'],
                    numero_huespedes=d['numero_huespedes'],
                    creada_por=request.user, observaciones=d['observaciones'])
            except ErrorNegocio as error:
                messages.error(request, str(error))
                return self.render(request, huesped_form, estadia_form)
            messages.success(request, f'Reserva {reserva.codigo} creada correctamente.')
            return redirect('mis_reservas' if request.user.es_cliente else 'reservas')
        return self.render(request, huesped_form, estadia_form)

    def render(self, request, huesped_form, estadia_form):
        contexto = self.get_context_data(huesped_form=huesped_form, estadia_form=estadia_form)
        contexto['pagina_titulo'] = 'Nueva reserva'
        contexto['puede_ver_tarifa'] = not request.user.es_cliente
        if estadia_form.is_valid():
            contexto['resumen'] = estadia_form.resumen()
        return render(request, self.template_name, contexto)


class MisReservasView(RolRequeridoMixin, ListView):
    """UI-05 (cliente). Consulta sus reservas y solicita cancelaciones (CU-09)."""
    roles = ROLES_POR_URL['mis_reservas']
    template_name = 'reservas/mis_reservas.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        huesped = getattr(self.request.user, 'huesped', None)
        if huesped is None:
            return Reserva.objects.none()
        return (Reserva.objects.filter(huesped=huesped)
                .select_related('habitacion', 'habitacion__tipo_habitacion')
                .order_by('-creado_en', '-id'))

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        if accion == 'solicitar' and pk:
            return self.solicitar_cancelacion(request, pk)
        return super().get(request, *args, **kwargs)

    def solicitar_cancelacion(self, request, pk):
        huesped = getattr(request.user, 'huesped', None)
        reserva = Reserva.objects.filter(pk=pk, huesped=huesped).first()
        if reserva is None:
            messages.error(request, 'La reserva no existe o no pertenece a tu cuenta.')
            return redirect(reverse('mis_reservas'))
        if reserva.estado not in rl.MODIFICABLES:
            messages.error(request, f'Una reserva {reserva.get_estado_display().lower()} '
                                     'no se puede cancelar.')
            return redirect(reverse('mis_reservas'))
        if reserva.solicitudes_cancelacion.filter(
                estado=SolicitudCancelacion.PENDIENTE).exists():
            messages.error(request, 'Ya tienes una solicitud pendiente para esta reserva.')
            return redirect(reverse('mis_reservas'))
        motivo = request.GET.get('motivo', '').strip()
        if not motivo:
            messages.error(request, 'Debes escribir el motivo de la solicitud.')
            return redirect(reverse('mis_reservas'))
        SolicitudCancelacion.objects.create(
            reserva=reserva, solicitada_por=request.user, motivo=motivo)
        messages.success(request, f'Solicitud enviada para la reserva {reserva.codigo}. '
                                  'El personal la revisará.')
        return redirect(reverse('mis_reservas'))

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['pagina_titulo'] = 'Mis reservas'
        contexto['filas'] = []
        for reserva in contexto['reservas']:
            solicitud = (reserva.solicitudes_cancelacion
                          .exclude(estado=SolicitudCancelacion.RECHAZADA)
                          .order_by('-fecha_solicitud').first())
            contexto['filas'].append({'reserva': reserva, 'solicitud': solicitud})
        return contexto
