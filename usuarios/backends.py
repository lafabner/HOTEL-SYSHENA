from django.contrib.auth import get_user_model
from django.contrib.auth.backends import AllowAllUsersModelBackend


class EmailOUsernameBackend(AllowAllUsersModelBackend):
    """Permite iniciar sesión con el nombre de usuario o con el correo.
    Deja pasar a las cuentas inactivas para que el formulario muestre
    el mensaje 'cuenta no habilitada' (CU-01, flujo alterno)."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()
        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        if not username or password is None:
            return None
        usuario = (Usuario.objects.filter(username=username).first()
                   or Usuario.objects.filter(email__iexact=username).first())
        if usuario is None:
            Usuario().set_password(password)   # igualar tiempos de respuesta
            return None
        if usuario.check_password(password):
            return usuario
        return None
