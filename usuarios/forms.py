import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Usuario

# Atributos para campos que solo aceptan números (documento, teléfono)
ATTRS_NUMERICOS = {
    'inputmode': 'numeric',
    'pattern': '[0-9]*',
    'autocomplete': 'off',
    'data-solo-numeros': '',
}


def validar_solo_digitos(nombre_campo, valor, minimo=5, maximo=15):
    """Validación compartida: solo dígitos y longitud razonable."""
    valor = (valor or '').strip()
    if not valor:
        return valor
    if not re.fullmatch(r'\d{%d,%d}' % (minimo, maximo), valor):
        raise forms.ValidationError(
            f'El {nombre_campo} solo acepta números ({minimo} a {maximo} dígitos), '
            'sin letras, espacios ni guiones.')
    return valor


class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'El usuario o correo y la contraseña no coinciden. Verifica los datos.',
        'inactive': 'Tu cuenta no está habilitada. Comunícate con el administrador.',
    }
    username = forms.CharField(
        label='Correo o usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True,
                                      'autocomplete': 'username', 'id': 'id_username'}))
    password = forms.CharField(
        label='Contraseña', strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'autocomplete': 'current-password', 'id': 'id_password'}))
    recordarme = forms.BooleanField(required=False, label='Recordarme')


class UsuarioForm(forms.ModelForm):
    """Alta de cuentas de usuario desde la pantalla Usuarios y roles."""
    password = forms.CharField(
        label='Contraseña', min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}))

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(
                attrs={'class': 'form-control', **ATTRS_NUMERICOS}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_telefono(self):
        return validar_solo_digitos('teléfono', self.cleaned_data.get('telefono'),
                                    minimo=7, maximo=15)


class RegistroClienteForm(forms.Form):
    """Registro público: crea el usuario con rol CLIENTE y su ficha de huésped."""
    nombres = forms.CharField(label='Nombres', max_length=100,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(label='Apellidos', max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('TI', 'Tarjeta de identidad'),
        ('PAS', 'Pasaporte'),
    ]
    tipo_documento = forms.ChoiceField(label='Tipo de documento', choices=TIPOS_DOCUMENTO,
                                      widget=forms.Select(attrs={'class': 'form-select'}))
    numero_documento = forms.CharField(
        label='Número de documento', max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', **ATTRS_NUMERICOS}))
    telefono = forms.CharField(label='Teléfono', max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', **ATTRS_NUMERICOS}))
    correo = forms.EmailField(label='Correo electrónico',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Contraseña', min_length=8,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_password = forms.CharField(label='Confirmar contraseña',
                                         widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_correo(self):
        correo = self.cleaned_data['correo'].lower()
        if Usuario.objects.filter(email__iexact=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return correo

    def clean_numero_documento(self):
        return validar_solo_digitos('número de documento',
                                   self.cleaned_data.get('numero_documento'))

    def clean_telefono(self):
        return validar_solo_digitos('teléfono', self.cleaned_data.get('telefono'),
                                    minimo=7, maximo=15)

    def clean(self):
        datos = super().clean()
        if datos.get('password') and datos.get('confirmar_password'):
            if datos['password'] != datos['confirmar_password']:
                self.add_error('confirmar_password', 'Las contraseñas no coinciden.')
        from huespedes.models import Huesped
        doc = datos.get('numero_documento')
        tipo = datos.get('tipo_documento')
        if doc and tipo and Huesped.objects.filter(
                tipo_documento=tipo, numero_documento=doc).exists():
            self.add_error('numero_documento',
                           'Ya existe un huésped con ese documento.')
        return datos
