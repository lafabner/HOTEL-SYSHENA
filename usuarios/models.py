from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from core.models import ModeloBase


class Rol(ModeloBase):
    ADMINISTRADOR = 'ADMINISTRADOR'
    RECEPCIONISTA = 'RECEPCIONISTA'
    CLIENTE = 'CLIENTE'
    GERENTE = 'GERENTE'
    OPCIONES = [
        (ADMINISTRADOR, 'Administrador'),
        (RECEPCIONISTA, 'Recepcionista'),
        (CLIENTE, 'Cliente'),
        (GERENTE, 'Gerente'),
    ]

    nombre = models.CharField(max_length=30, unique=True, choices=OPCIONES)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'rol'
        verbose_name_plural = 'roles'
        ordering = ['nombre']

    def __str__(self):
        return self.get_nombre_display()


class UsuarioManager(UserManager):
    """Si no se indica rol: usuario normal = CLIENTE, superusuario = ADMINISTRADOR."""

    def create_user(self, username, email=None, password=None, **extra_fields):
        if 'rol' not in extra_fields and 'rol_id' not in extra_fields:
            extra_fields['rol'], _ = Rol.objects.get_or_create(nombre=Rol.CLIENTE)
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if 'rol' not in extra_fields and 'rol_id' not in extra_fields:
            extra_fields['rol'], _ = Rol.objects.get_or_create(nombre=Rol.ADMINISTRADOR)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    email = models.EmailField('correo electrónico', max_length=254, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios')

    objects = UsuarioManager()
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_administrador(self):
        return self.rol.nombre == Rol.ADMINISTRADOR

    @property
    def es_recepcionista(self):
        return self.rol.nombre == Rol.RECEPCIONISTA

    @property
    def es_cliente(self):
        return self.rol.nombre == Rol.CLIENTE

    @property
    def es_gerente(self):
        return self.rol.nombre == Rol.GERENTE