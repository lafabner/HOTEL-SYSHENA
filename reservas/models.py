import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from core.models import ModeloBase
from habitaciones.models import Habitacion
from huespedes.models import Huesped


class Reserva(ModeloBase):
    PENDIENTE = 'PENDIENTE'
    CONFIRMADA = 'CONFIRMADA'
    EN_ESTADIA = 'EN_ESTADIA'
    CANCELADA = 'CANCELADA'
    FINALIZADA = 'FINALIZADA'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (CONFIRMADA, 'Confirmada'),
        (EN_ESTADIA, 'En estadía'),
        (CANCELADA, 'Cancelada'),
        (FINALIZADA, 'Finalizada'),
    ]
    # Estados que bloquean la disponibilidad de la habitación
    ESTADOS_BLOQUEANTES = [PENDIENTE, CONFIRMADA, EN_ESTADIA]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, related_name='reservas')
    habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='reservas')
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   related_name='reservas_creadas')
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    numero_huespedes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    tarifa_noche = models.DecimalField(max_digits=12, decimal_places=2)
    valor_hospedaje = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    valor_servicios = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    valor_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'
        ordering = ['-fecha_entrada', '-id']
        indexes = [
            models.Index(fields=['habitacion', 'fecha_entrada', 'fecha_salida'], name='idx_reserva_disponibilidad'),
            models.Index(fields=['estado'], name='idx_reserva_estado'),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(fecha_salida__gt=models.F('fecha_entrada')),
                                   name='ck_reserva_salida_posterior'),
            models.CheckConstraint(condition=models.Q(numero_huespedes__gt=0),
                                   name='ck_reserva_huespedes_positivos'),
            models.CheckConstraint(condition=models.Q(tarifa_noche__gte=0),
                                   name='ck_reserva_tarifa_no_negativa'),
        ]

    def __str__(self):
        return self.codigo or 'Reserva nueva'

    @property
    def noches(self):
        return (self.fecha_salida - self.fecha_entrada).days

    @property
    def activa(self):
        return self.estado in self.ESTADOS_BLOQUEANTES

    def clean(self):
        if self.fecha_entrada and self.fecha_salida and self.fecha_salida <= self.fecha_entrada:
            raise ValidationError({'fecha_salida': 'La fecha de salida debe ser posterior a la de entrada.'})
        if self.habitacion_id and self.numero_huespedes and self.numero_huespedes > self.habitacion.capacidad:
            raise ValidationError({'numero_huespedes': 'Supera la capacidad de la habitación '
                                                       f'({self.habitacion.capacidad}).'})

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Código temporal único; luego se reemplaza por RES-AAAA-00001
            self.codigo = uuid.uuid4().hex[:20]
            if self.tarifa_noche in (None, ''):
                self.tarifa_noche = self.habitacion.precio_noche
            super().save(*args, **kwargs)
            self.codigo = f'RES-{timezone.now():%Y}-{self.pk:05d}'
            self.recalcular_totales(guardar=False)
            kwargs.pop('force_insert', None)
            super().save(update_fields=['codigo', 'valor_hospedaje', 'valor_total', 'saldo_pendiente'])
        else:
            super().save(*args, **kwargs)

    def recalcular_totales(self, guardar=True):
        """valor_total = hospedaje + servicios | saldo = total - pagado"""
        servicios = self.consumos.aggregate(t=Sum('subtotal'))['t'] or Decimal('0')
        pagado = self.pagos.aggregate(t=Sum('valor'))['t'] or Decimal('0') if self.pk else Decimal('0')
        self.valor_hospedaje = self.tarifa_noche * self.noches
        self.valor_servicios = servicios
        self.valor_total = self.valor_hospedaje + self.valor_servicios
        self.valor_pagado = pagado
        self.saldo_pendiente = self.valor_total - self.valor_pagado
        if guardar:
            self.save(update_fields=['valor_hospedaje', 'valor_servicios', 'valor_total',
                                     'valor_pagado', 'saldo_pendiente', 'actualizado_en'])


class SolicitudCancelacion(models.Model):
    PENDIENTE = 'PENDIENTE'
    APROBADA = 'APROBADA'
    RECHAZADA = 'RECHAZADA'
    ESTADOS = [(PENDIENTE, 'Pendiente'), (APROBADA, 'Aprobada'), (RECHAZADA, 'Rechazada')]

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='solicitudes_cancelacion')
    solicitada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                       related_name='solicitudes_cancelacion')
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    resuelta_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True,
                                     null=True, related_name='solicitudes_resueltas')
    fecha_resolucion = models.DateTimeField(blank=True, null=True)
    respuesta = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'solicitud de cancelación'
        verbose_name_plural = 'solicitudes de cancelación'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'{self.reserva.codigo} - {self.get_estado_display()}'