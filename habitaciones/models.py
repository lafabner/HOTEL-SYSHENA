from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from alojamientos.models import Alojamiento


class TipoHabitacion(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='tipos_habitacion')
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'tipo de habitación'
        verbose_name_plural = 'tipos de habitación'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['alojamiento', 'nombre'], name='uq_tipo_alojamiento_nombre'),
        ]

    def __str__(self):
        return self.nombre


class Habitacion(models.Model):
    DISPONIBLE = 'DISPONIBLE'
    OCUPADA = 'OCUPADA'
    MANTENIMIENTO = 'MANTENIMIENTO'
    ESTADOS = [
        (DISPONIBLE, 'Disponible'),
        (OCUPADA, 'Ocupada'),
        (MANTENIMIENTO, 'Mantenimiento'),
    ]

    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='habitaciones')
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name='habitaciones')
    numero = models.CharField(max_length=20)
    capacidad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    precio_noche = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    piso = models.SmallIntegerField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=DISPONIBLE)
    activa = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'habitación'
        verbose_name_plural = 'habitaciones'
        ordering = ['numero']
        constraints = [
            models.UniqueConstraint(fields=['alojamiento', 'numero'], name='uq_habitacion_alojamiento_numero'),
            models.CheckConstraint(condition=models.Q(capacidad__gt=0), name='ck_habitacion_capacidad_positiva'),
            models.CheckConstraint(condition=models.Q(precio_noche__gte=0), name='ck_habitacion_precio_no_negativo'),
        ]

    def __str__(self):
        return f'Habitación {self.numero} - {self.tipo_habitacion}'

    def clean(self):
        if self.tipo_habitacion_id and self.alojamiento_id:
            if self.tipo_habitacion.alojamiento_id != self.alojamiento_id:
                raise ValidationError('El tipo de habitación pertenece a otro alojamiento.')