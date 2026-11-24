from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'valor', 'metodo', 'referencia', 'fecha_hora')
    list_filter = ('metodo',)