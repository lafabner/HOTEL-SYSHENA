from datetime import date, timedelta

from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone

from core.navegacion import ROLES_POR_URL
from core.permisos import RolRequeridoMixin
from usuarios.models import Rol

from .indicadores import calcular_dashboard, calcular_reportes


class DashboardView(RolRequeridoMixin, TemplateView):
    """UI-02. Visible para Administrador y Gerente."""
    roles = (Rol.ADMINISTRADOR, Rol.GERENTE)
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(calcular_dashboard())
        contexto['pagina_titulo'] = 'Dashboard'
        contexto['puede_crear_reserva'] = self.request.user.rol.nombre == Rol.ADMINISTRADOR
        return contexto


class ReportesView(RolRequeridoMixin, TemplateView):
    """UI-10. Reportes por periodo para Administrador y Gerente."""
    roles = (Rol.ADMINISTRADOR, Rol.GERENTE)
    template_name = 'reportes/reportes.html'

    def get(self, request, *args, **kwargs):
        hoy = timezone.localdate()
        desde_str = request.GET.get('desde', '')
        hasta_str = request.GET.get('hasta', '')
        try:
            desde = date.fromisoformat(desde_str) if desde_str else hoy.replace(day=1)
            hasta = date.fromisoformat(hasta_str) if hasta_str else desde + timedelta(days=30)
        except ValueError:
            desde, hasta = hoy.replace(day=1), hoy
        datos = calcular_reportes(desde, hasta) if desde <= hasta else None
        contexto = self.get_context_data(
            datos=datos, desde=desde, hasta=hasta, error=desde > hasta)
        contexto['pagina_titulo'] = 'Reportes'
        return render(request, self.template_name, contexto)
