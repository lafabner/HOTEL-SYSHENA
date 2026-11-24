from django.conf import settings
from django.db import models

from core.models import ModeloBase


class Huesped(ModeloBase):
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('TI', 'Tarjeta de identidad'),
        ('PAS', 'Pasaporte'),
        ('PPT', 'Permiso por protección temporal'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='huesped',
    )
    tipo_documento = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO, default='CC')
    numero_documento = models.CharField(max_length=30)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=254, blank=True, null=True)
    nacionalidad = models.CharField(max_length=80, default='Colombiana')
    contacto_emergencia = models.CharField(max_length=150, blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'huésped'
        verbose_name_plural = 'huéspedes'
        ordering = ['apellidos', 'nombres']
        constraints = [
            models.UniqueConstraint(fields=['tipo_documento', 'numero_documento'], name='uq_huesped_documento'),
        ]

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    def __str__(self):
        return f'{self.nombre_completo} ({self.tipo_documento} {self.numero_documento})'