from django.contrib import admin

from .models import Estadia


@admin.register(Estadia)
class EstadiaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'fecha_hora_checkin', 'fecha_hora_checkout', 'usuario_checkin')