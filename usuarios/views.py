from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from core.navegacion import INICIO_POR_ROL, ROLES_POR_URL
from core.permisos import RolRequeridoMixin

from .forms import LoginForm, RegistroClienteForm, UsuarioForm
from .models import Rol, Usuario


class RegistroView(TemplateView):
    """Registro público de clientes: crea la cuenta y su ficha de huésped."""
    template_name = 'publico/registro.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(INICIO_POR_ROL[request.user.rol.nombre])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render(request, RegistroClienteForm())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            usuario = Usuario.objects.create_user(
                username=d['correo'].lower(), email=d['correo'].lower(),
                password=d['password'], first_name=d['nombres'],
                last_name=d['apellidos'], telefono=d['telefono'],
                rol=Rol.objects.get_or_create(nombre=Rol.CLIENTE)[0])
            from huespedes.models import Huesped
            Huesped.objects.create(
                usuario=usuario, tipo_documento=d['tipo_documento'],
                numero_documento=d['numero_documento'], nombres=d['nombres'],
                apellidos=d['apellidos'], telefono=d['telefono'], correo=d['correo'].lower())
            login(request, usuario, backend='usuarios.backends.EmailOUsernameBackend')
            messages.success(request, f'¡Bienvenido, {d["nombres"]}! Tu cuenta está lista.')
            return redirect(INICIO_POR_ROL[usuario.rol.nombre])
        return self.render(request, form)

    def render(self, request, form):
        contexto = self.get_context_data(form=form)
        contexto['pagina_titulo'] = 'Crear cuenta'
        return render(request, self.template_name, contexto)


class LoginView(auth_views.LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse(INICIO_POR_ROL[self.request.user.rol.nombre])

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        if not form.cleaned_data.get('recordarme'):
            self.request.session.set_expiry(0)   # la sesión termina al cerrar el navegador
        return respuesta


class UsuariosView(RolRequeridoMixin, TemplateView):
    """UI-09. Cuentas de usuario, roles y estado. Solo administradores."""
    roles = ROLES_POR_URL['usuarios']
    template_name = 'usuarios/usuarios.html'

    def get(self, request, *args, **kwargs):
        accion = request.GET.get('accion', '')
        pk = request.GET.get('pk', '')
        if accion and pk:
            return self.ejecutar_accion(request, accion, pk)
        return self.render(request, UsuarioForm())

    def post(self, request, *args, **kwargs):
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} creado con rol '
                                      f'{usuario.rol.get_nombre_display()}.')
            return redirect(reverse('usuarios'))
        return self.render(request, form)

    def ejecutar_accion(self, request, accion, pk):
        usuario = Usuario.objects.filter(pk=pk).first()
        if usuario is None:
            messages.error(request, 'El usuario no existe.')
            return redirect(reverse('usuarios'))
        if accion == 'rol':
            rol = Rol.objects.filter(nombre=request.GET.get('rol', ''), activo=True).first()
            if rol is None:
                messages.error(request, 'Ese rol no existe.')
            elif usuario.pk == request.user.pk and rol.nombre != Rol.ADMINISTRADOR:
                messages.error(request, 'No puedes quitarte tu propio rol de administrador.')
            else:
                usuario.rol = rol
                usuario.save(update_fields=['rol'])
                messages.success(request, f'Rol de {usuario.username} cambiado a '
                                          f'{rol.get_nombre_display()}.')
        elif accion in ('activar', 'desactivar'):
            if usuario.pk == request.user.pk:
                messages.error(request, 'No puedes desactivar tu propia cuenta.')
            else:
                usuario.is_active = accion == 'activar'
                usuario.save(update_fields=['is_active'])
                estado = 'activada' if usuario.is_active else 'desactivada'
                messages.success(request, f'Cuenta {usuario.username} {estado}.')
        else:
            messages.error(request, 'Acción no permitida.')
        return redirect(reverse('usuarios'))

    def render(self, request, form):
        contexto = self.get_context_data(form=form)
        contexto['pagina_titulo'] = 'Usuarios y roles'
        contexto['usuarios_lista'] = (Usuario.objects.select_related('rol')
                                      .order_by('username'))
        contexto['roles'] = Rol.objects.filter(activo=True).order_by('nombre')
        return render(request, self.template_name, contexto)
