from django.contrib import admin

from pagos.models import Pago
from servicios.models import ServicioReserva

from .models import Reserva, SolicitudCancelacion


class ConsumoInline(admin.TabularInline):
    model = ServicioReserva
    extra = 0
    readonly_fields = ('subtotal', 'fecha_hora')


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 0
    readonly_fields = ('fecha_hora',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'huesped', 'habitacion', 'fecha_entrada', 'fecha_salida',
                    'estado', 'valor_total', 'saldo_pendiente')
    list_filter = ('estado', 'fecha_entrada')
    search_fields = ('codigo', 'huesped__nombres', 'huesped__apellidos', 'huesped__numero_documento')
    readonly_fields = ('codigo', 'valor_hospedaje', 'valor_servicios', 'valor_total',
                       'valor_pagado', 'saldo_pendiente')
    inlines = [ConsumoInline, PagoInline]


@admin.register(SolicitudCancelacion)
class SolicitudCancelacionAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'solicitada_por', 'estado', 'fecha_solicitud')
    list_filter = ('estado',)