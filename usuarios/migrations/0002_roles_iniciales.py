from django.db import migrations

ROLES = [
    ('ADMINISTRADOR', 'Configura el sistema y administra catálogos, usuarios, habitaciones y servicios'),
    ('RECEPCIONISTA', 'Ejecuta reservas y la operación diaria del alojamiento'),
    ('CLIENTE', 'Consulta disponibilidad y gestiona sus propias reservas'),
    ('GERENTE', 'Consulta indicadores, estadísticas y reportes'),
]


def crear_roles(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    for nombre, descripcion in ROLES:
        Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion, 'activo': True})


class Migration(migrations.Migration):
    dependencies = [('usuarios', '0001_initial')]
    operations = [migrations.RunPython(crear_roles, migrations.RunPython.noop)]