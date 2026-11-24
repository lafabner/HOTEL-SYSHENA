from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView

from .clases import clase_estado_habitacion

from core.errores import ErrorNegocio
from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin
from reservas.models import Reserva

from .forms import DisponibilidadForm
from .models import Habitacion, TipoHabitacion

CLASE_ESTADO = {
    Habitacion.DISPONIBLE: 'available',
    Habitacion.OCUPADA: 'occupied',
    Habitacion.MANTENIMIENTO: 'pending',
}

ESTADOS_NO_EDITABLES = (Habitacion.OCUPADA,)


class HabitacionesView(RolRequeridoMixin, ListView):
    """UI-06. Inventario de habitaciones y estados operativos (CU-10)."""
    roles = ROLES_POR_URL['habitaciones']
    template_name = 'habitaciones/habitaciones.html'
    context_object_name = 'habitaciones'

    def get_queryset(self):
        qs = (Habitacion.objects.filter(activa=True)
              .select_related('tipo_habitacion', 'alojamiento')
              .annotate(reservas_activas=Count(
                  'reservas',
                  filter=Q(reservas__estado__in=Reserva.ESTADOS_BLOQUEANTES))))
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(numero__icontains=q) | Q(tipo_habitacion__nombre__icontains=q))
        estado = self.request.GET.get('estado', '')
        if estado:
            qs = qs.filter(estado=estado)
        tipo = self.request.GET.get('tipo', '')
        if tipo:
            qs = qs.filter(tipo_habitacion__nombre=tipo)
        return qs.order_by('alojamiento__nombre', 'numero')

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        estado_nuevo = request.GET.get('estado_nuevo', '')
        if accion == 'cambiar_estado' and pk and estado_nuevo:
            return self.cambiar_estado(request, pk, estado_nuevo)
        return super().get(request, *args, **kwargs)

    def cambiar_estado(self, request, pk, estado_nuevo):
        habitacion = Habitacion.objects.filter(pk=pk).first()
        if habitacion is None:
            messages.error(request, 'La habitación no existe.')
            return redirect(reverse('habitaciones'))
        try:
            if estado_nuevo in ESTADOS_NO_EDITABLES:
                raise ErrorNegocio('El estado "Ocupada" se gestiona con el check-in de una reserva.')
            habitacion.cambiar_estado(estado_nuevo)
            messages.success(request, f'Habitación {habitacion.numero} ahora está '
                                       f'{habitacion.get_estado_display().lower()}.')
        except ErrorNegocio as error:
            messages.error(request, str(error))
        return redirect(reverse('habitaciones'))

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['pagina_titulo'] = 'Habitaciones'
        contexto['estados'] = [e for e in Habitacion.ESTADOS if e[0] != Habitacion.OCUPADA]
        contexto['tipos'] = list(TipoHabitacion.objects.filter(activo=True)
                                 .values_list('nombre', flat=True))
        contexto['q_actual'] = self.request.GET.get('q', '')
        contexto['estado_actual'] = self.request.GET.get('estado', '')
        contexto['tipo_actual'] = self.request.GET.get('tipo', '')
        rol = getattr(self.request.user, 'rol', None)
        contexto['puede_editar'] = rol and rol.nombre in ('ADMINISTRADOR', 'RECEPCIONISTA')
        for h in contexto['habitaciones']:
            h.clase_estado = clase_estado_habitacion(h.estado)
        return contexto


class DisponibilidadView(RolRequeridoMixin, ListView):
    """UI-03. Habitaciones libres por fechas, capacidad y tipo (CU-06)."""
    roles = ROLES_POR_URL['disponibilidad']
    template_name = 'habitaciones/disponibilidad.html'
    context_object_name = 'habitaciones'

    def get(self, request, *args, **kwargs):
        if not request.GET:                     # primera visita: solo filtros
            return render(request, self.template_name,
                         {'form': DisponibilidadForm(), 'pagina_titulo': 'Disponibilidad'})
        return super().get(request, *args, **kwargs)

    def get_form(self):
        return DisponibilidadForm(self.request.GET)

    def get_queryset(self):
        form = self.get_form()
        if not form.is_valid():
            return None
        d = form.cleaned_data
        try:
            from reservas import logica as rl
            return rl.habitaciones_disponibles(
                d['fecha_entrada'], d['fecha_salida'], d['huespedes'],
                tipo=d['tipo_habitacion'])
        except ErrorNegocio as error:
            messages.error(self.request, str(error))
            return None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        form = self.get_form()
        contexto['form'] = form
        contexto['pagina_titulo'] = 'Disponibilidad'
        contexto['es_valido'] = form.is_valid()
        if form.is_valid():
            d = form.cleaned_data
            contexto['ingreso'] = d['fecha_entrada']
            contexto['salida'] = d['fecha_salida']
            contexto['huespedes_buscados'] = d['huespedes']
            contexto['total'] = self.object_list.count() if self.object_list is not None else 0
        return contexto
