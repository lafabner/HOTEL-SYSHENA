from django.contrib import admin

from .models import Servicio, ServicioReserva


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'alojamiento', 'precio', 'activo')
    list_filter = ('activo',)


@admin.register(ServicioReserva)
class ServicioReservaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'servicio', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_hora')