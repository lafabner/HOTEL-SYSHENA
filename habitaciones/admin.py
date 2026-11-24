from django.contrib import admin

from .models import Habitacion, TipoHabitacion


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'alojamiento', 'activo')


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo_habitacion', 'capacidad', 'precio_noche', 'piso', 'estado', 'activa')
    list_filter = ('estado', 'activa', 'tipo_habitacion')
    search_fields = ('numero',)