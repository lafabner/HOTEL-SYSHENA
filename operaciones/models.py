from django.conf import settings
from django.db import models

from reservas.models import Reserva


class Estadia(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.PROTECT, related_name='estadia')
    usuario_checkin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                        related_name='checkins_realizados')
    usuario_checkout = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True,
                                         null=True, related_name='checkouts_realizados')
    fecha_hora_checkin = models.DateTimeField()
    fecha_hora_checkout = models.DateTimeField(blank=True, null=True)
    observaciones_checkin = models.TextField(blank=True, null=True)
    observaciones_checkout = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'estadía'
        verbose_name_plural = 'estadías'
        ordering = ['-fecha_hora_checkin']

    def __str__(self):
        return f'Estadía {self.reserva.codigo}'
