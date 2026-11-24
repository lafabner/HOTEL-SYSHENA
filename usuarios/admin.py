from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Rol, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo')


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    fieldsets = UserAdmin.fieldsets + (('SysHSENA', {'fields': ('rol', 'telefono')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SysHSENA', {'fields': ('email', 'rol', 'telefono')}),
    )