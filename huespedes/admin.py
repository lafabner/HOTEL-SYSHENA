from django.contrib import admin

from .models import Huesped


@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'tipo_documento', 'numero_documento', 'telefono', 'correo')
    search_fields = ('nombres', 'apellidos', 'numero_documento')
    list_filter = ('tipo_documento',)