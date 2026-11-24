from django.db.models import Count, Q
from django.views.generic import ListView

from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin

from .models import Huesped


class HuespedesView(RolRequeridoMixin, ListView):
    """UI-07. Lista de huéspedes con búsqueda y contacto."""
    roles = ROLES_POR_URL['huespedes']
    template_name = 'huespedes/huespedes.html'
    context_object_name = 'huespedes'
    paginate_by = 20

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        qs = Huesped.objects.annotate(total_reservas=Count('reservas'))
        if q:
            qs = qs.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q)
                           | Q(numero_documento__icontains=q) | Q(correo__icontains=q))
        return qs.order_by('apellidos', 'nombres')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['pagina_titulo'] = 'Huéspedes'
        contexto['q_actual'] = self.request.GET.get('q', '')
        return contexto
