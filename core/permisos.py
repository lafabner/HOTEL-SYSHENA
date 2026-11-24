from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class RolRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Exige sesión iniciada y que el rol del usuario esté en `roles`.
    La autorización se verifica siempre en el servidor."""
    roles = ()

    def test_func(self):
        usuario = self.request.user
        return usuario.is_active and usuario.rol.nombre in self.roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied
