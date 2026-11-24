from django.contrib import messages
from django.db.models import Max, Min
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import TemplateView

from alojamientos.forms import AlojamientoForm
from alojamientos.models import Alojamiento
from habitaciones.models import TipoHabitacion
from servicios.models import Servicio

from .navegacion import INICIO_POR_ROL
from .permisos import RolRequeridoMixin
from .contenido_publico import (
    HERO_MEDIA, PRESENTACION, DESCRIPCIONES_HABITACION, DESCRIPCIONES_SERVICIO,
)


def inicio(request):
    """Portada pública accesible también con sesión iniciada."""
    if request.user.is_authenticated and request.GET.get('panel') == '1':
        return redirect(INICIO_POR_ROL[request.user.rol.nombre])
    from habitaciones.models import Habitacion
    alojamiento = Alojamiento.objects.filter(activo=True).select_related('municipio').first()
    foto_real = None
    tipos = servicios = sitios = estadisticas = None
    if alojamiento:
        tipos = (TipoHabitacion.objects
                 .filter(activo=True, alojamiento=alojamiento)
                 .filter(habitaciones__activa=True)
                 .annotate(precio_min=Min('habitaciones__precio_noche'),
                           capacidad_max=Max('habitaciones__capacidad'))
                 .order_by('precio_min').distinct())
        servicios = Servicio.objects.filter(activo=True, alojamiento=alojamiento)
        sitios = alojamiento.sitios_turisticos.filter(activo=True)
        foto_real = alojamiento.fotos.order_by('-principal', 'orden', 'id').first()
        estadisticas = {
            'habitaciones': Habitacion.objects.filter(activa=True, alojamiento=alojamiento).count(),
            'servicios': servicios.count(),
            'sitios': sitios.count(),
        }
        for tipo in tipos:
            nombre = slugify(tipo.nombre)
            tipo.detalle_publico = next(
                (texto for clave, texto in DESCRIPCIONES_HABITACION.items() if clave in nombre),
                'Compara la capacidad y la tarifa de esta opción. Consulta con recepción la distribución del espacio antes de reservar.')
        for servicio in servicios:
            nombre = slugify(servicio.nombre)
            servicio.detalle_publico = next(
                (texto for clave, texto in DESCRIPCIONES_SERVICIO.items() if clave in nombre),
                'Confirma con recepción la disponibilidad, las condiciones y la unidad de cobro de este servicio antes de solicitarlo.')
    hero_media = [dict(item) for item in HERO_MEDIA]
    if foto_real:
        hero_media.insert(0, {
            'tipo': 'imagen_real', 'archivo': foto_real.imagen.url,
            'etiqueta': alojamiento.nombre, 'titulo': 'Tu estancia.\nTu punto de partida.',
            'texto': 'Conoce el alojamiento y empieza a planear tu visita.',
            'accion': 'Conoce nuestra propuesta', 'ancla': '#nosotros',
            'nota': foto_real.texto_alternativo, 'poster': '',
        })
    return render(request, 'publico/inicio.html', {
        'alojamiento': alojamiento,
        'tipos': tipos,
        'servicios': servicios,
        'sitios': sitios,
        'estadisticas': estadisticas,
        'foto_real': foto_real,
        'hoy': timezone.localdate(),
        'panel_usuario': INICIO_POR_ROL.get(request.user.rol.nombre, 'mis_reservas')
            if request.user.is_authenticated else None,
        'presentacion': PRESENTACION,
        'hero_media': hero_media,
    })


class ConfiguracionView(RolRequeridoMixin, TemplateView):
    """UI-10. Datos del alojamiento, contacto y horarios. Solo administradores."""
    template_name = 'core/configuracion.html'
    roles = ['ADMINISTRADOR']

    def get(self, request, *args, **kwargs):
        alojamiento = Alojamiento.objects.select_related('municipio').first()
        if alojamiento is None:
            messages.error(request, 'Aún no hay alojamiento creado. Usa '
                                    '"python manage.py cargar_datos" o créalo '
                                    'desde el admin de Django.')
            return redirect(reverse('dashboard'))
        contexto = self.get_context_data(form=AlojamientoForm(instance=alojamiento))
        contexto['pagina_titulo'] = 'Configuración'
        contexto['alojamiento'] = alojamiento
        return render(request, self.template_name, contexto)

    def post(self, request, *args, **kwargs):
        alojamiento = Alojamiento.objects.select_related('municipio').first()
        form = AlojamientoForm(request.POST, instance=alojamiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del alojamiento actualizados.')
            return redirect(reverse('configuracion'))
        contexto = self.get_context_data(form=form)
        contexto['pagina_titulo'] = 'Configuración'
        contexto['alojamiento'] = alojamiento
        return render(request, self.template_name, contexto)
