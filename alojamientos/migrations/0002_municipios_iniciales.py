from django.db import migrations

MUNICIPIOS = [
    'Riohacha', 'Albania', 'Barrancas', 'Dibulla', 'Distracción', 'El Molino',
    'Fonseca', 'Hatonuevo', 'La Jagua del Pilar', 'Maicao', 'Manaure',
    'San Juan del Cesar', 'Uribia', 'Urumita', 'Villanueva',
]


def crear_municipios(apps, schema_editor):
    Municipio = apps.get_model('alojamientos', 'Municipio')
    for nombre in MUNICIPIOS:
        Municipio.objects.get_or_create(nombre=nombre, departamento='La Guajira', defaults={'activo': True})


class Migration(migrations.Migration):
    dependencies = [('alojamientos', '0001_initial')]
    operations = [migrations.RunPython(crear_municipios, migrations.RunPython.noop)]