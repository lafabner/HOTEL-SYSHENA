from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from reservas.models import Reserva


class Pago(models.Model):
    EFECTIVO = 'EFECTIVO'
    TARJETA = 'TARJETA'
    TRANSFERENCIA = 'TRANSFERENCIA'
    OTRO = 'OTRO'
    METODOS = [
        (EFECTIVO, 'Efectivo'),
        (TARJETA, 'Tarjeta'),
        (TRANSFERENCIA, 'Transferencia'),
        (OTRO, 'Otro'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name='pagos')
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                       related_name='pagos_registrados')
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    metodo = models.CharField(max_length=20, choices=METODOS, default=EFECTIVO)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'pago'
        verbose_name_plural = 'pagos'
        ordering = ['-fecha_hora']
        constraints = [
            models.CheckConstraint(condition=models.Q(valor__gt=0), name='ck_pago_valor_positivo'),
        ]

    def __str__(self):
        return f'{self.reserva.codigo} - ${self.valor:,.0f}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.reserva.recalcular_totales()

    def delete(self, *args, **kwargs):
        reserva = self.reserva
        super().delete(*args, **kwargs)
        reserva.recalcular_totales()
