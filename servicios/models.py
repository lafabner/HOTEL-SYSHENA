from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from alojamientos.models import Alojamiento
from core.models import ModeloBase
from reservas.models import Reserva


class Servicio(ModeloBase):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'servicio'
        verbose_name_plural = 'servicios'
        ordering = ['nombre']
        constraints = [
            models.UniqueConstraint(fields=['alojamiento', 'nombre'], name='uq_servicio_alojamiento_nombre'),
            models.CheckConstraint(condition=models.Q(precio__gte=0), name='ck_servicio_precio_no_negativo'),
        ]

    def __str__(self):
        return self.nombre


class ServicioReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='consumos')
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name='consumos')
    cantidad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=Decimal('0'))
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                       related_name='consumos_registrados')
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'consumo de servicio'
        verbose_name_plural = 'consumos de servicios'
        ordering = ['-fecha_hora']
        constraints = [
            models.CheckConstraint(condition=models.Q(cantidad__gt=0), name='ck_consumo_cantidad_positiva'),
        ]

    def __str__(self):
        return f'{self.servicio} x{self.cantidad} ({self.reserva.codigo})'

    def save(self, *args, **kwargs):
        if self.precio_unitario is None:
            self.precio_unitario = self.servicio.precio   # precio histórico
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        self.reserva.recalcular_totales()

    def delete(self, *args, **kwargs):
        reserva = self.reserva
        super().delete(*args, **kwargs)
        reserva.recalcular_totales()