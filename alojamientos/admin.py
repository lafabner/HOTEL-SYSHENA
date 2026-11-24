from django.contrib import admin

from .models import Alojamiento, FotoAlojamiento, Municipio, SitioTuristico


class FotoInline(admin.TabularInline):
    model = FotoAlojamiento
    extra = 1


class SitioInline(admin.TabularInline):
    model = SitioTuristico
    extra = 1


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'departamento', 'activo')
    search_fields = ('nombre',)


@admin.register(Alojamiento)
class AlojamientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'municipio', 'telefono', 'activo')
    inlines = [FotoInline, SitioInline]