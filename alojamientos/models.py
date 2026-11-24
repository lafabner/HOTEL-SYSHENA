import datetime

from django.db import models

from core.models import ModeloBase


class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, default='La Guajira')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'departamento'], name='uq_municipio_nombre_depto'),
        ]

    def __str__(self):
        return f'{self.nombre}, {self.departamento}'


class Alojamiento(ModeloBase):
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, related_name='alojamientos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(max_length=254)
    informacion_turistica = models.TextField(blank=True, null=True)
    hora_checkin = models.TimeField(default=datetime.time(15, 0))
    hora_checkout = models.TimeField(default=datetime.time(12, 0))
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'alojamiento'
        verbose_name_plural = 'alojamientos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class FotoAlojamiento(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='alojamientos/')
    texto_alternativo = models.CharField(max_length=160)
    principal = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'foto del alojamiento'
        verbose_name_plural = 'fotos del alojamiento'
        ordering = ['orden', 'id']

    def __str__(self):
        return f'{self.alojamiento} - {self.texto_alternativo}'


class SitioTuristico(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='sitios_turisticos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    distancia_km = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'sitio turístico'
        verbose_name_plural = 'sitios turísticos'
        ordering = ['distancia_km', 'nombre']

    def __str__(self):
        return self.nombre