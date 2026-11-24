from django.core.management.base import BaseCommand

from alojamientos.models import Alojamiento, Municipio, SitioTuristico
from habitaciones.models import Habitacion, TipoHabitacion
from huespedes.models import Huesped
from servicios.models import Servicio
from usuarios.models import Rol, Usuario


class Command(BaseCommand):
    help = 'Carga datos de prueba de Posada Guajira Serena (se puede ejecutar varias veces).'

    def handle(self, *args, **options):
        # --- Alojamiento ---
        riohacha = Municipio.objects.get(nombre='Riohacha', departamento='La Guajira')
        posada, _ = Alojamiento.objects.get_or_create(
            nombre='Posada Guajira Serena',
            defaults={
                'municipio': riohacha,
                'descripcion': 'Posada frente al mar en Riohacha con ambiente familiar y servicio cercano.',
                'direccion': 'Calle 1 # 5-20, Riohacha',
                'telefono': '3001234567',
                'correo': 'info@posadaguajiraserena.co',
                'informacion_turistica': 'Cerca de la playa, el muelle turístico y el centro histórico.',
            },
        )

        # --- Sitios turísticos ---
        sitios = [
            ('Muelle turístico de Riohacha', 'Paseo frente al mar con restaurantes.', '0.80'),
            ('Santuario de Fauna y Flora Los Flamencos', 'Reserva natural con flamencos rosados.', '28.00'),
            ('Cabo de la Vela', 'Destino de playa y desierto en la alta Guajira.', '170.00'),
        ]
        for nombre, desc, km in sitios:
            SitioTuristico.objects.get_or_create(
                alojamiento=posada, nombre=nombre,
                defaults={'descripcion': desc, 'distancia_km': km},
            )

        # --- Tipos de habitación ---
        tipos = {}
        for nombre, desc in [
            ('Sencilla', 'Una cama, ideal para una persona.'),
            ('Doble', 'Cama doble o dos camas sencillas.'),
            ('Familiar', 'Espacio amplio para grupos familiares.'),
        ]:
            tipos[nombre], _ = TipoHabitacion.objects.get_or_create(
                alojamiento=posada, nombre=nombre, defaults={'descripcion': desc})

        # --- Habitaciones ---
        habitaciones = [
            ('101', 'Sencilla', 1, '90000', 1),
            ('102', 'Sencilla', 1, '90000', 1),
            ('103', 'Doble', 2, '140000', 1),
            ('201', 'Doble', 2, '140000', 2),
            ('202', 'Familiar', 4, '220000', 2),
            ('203', 'Familiar', 5, '260000', 2),
        ]
        for numero, tipo, cap, precio, piso in habitaciones:
            Habitacion.objects.get_or_create(
                alojamiento=posada, numero=numero,
                defaults={'tipo_habitacion': tipos[tipo], 'capacidad': cap,
                          'precio_noche': precio, 'piso': piso},
            )

        # --- Huéspedes ---
        for tipo_doc, num, nombres, apellidos, tel, correo in [
            ('CC', '1118500001', 'María', 'Pérez Gómez', '3105550001', 'maria@example.com'),
            ('CC', '1118500002', 'Carlos', 'Epieyú Uriana', '3105550002', 'carlos@example.com'),
            ('PAS', 'AB123456', 'John', 'Smith', '3105550003', 'john@example.com'),
        ]:
            Huesped.objects.get_or_create(
                tipo_documento=tipo_doc, numero_documento=num,
                defaults={'nombres': nombres, 'apellidos': apellidos, 'telefono': tel,
                          'correo': correo, 'nacionalidad': 'Estadounidense' if tipo_doc == 'PAS' else 'Colombiana'},
            )

                # --- Servicios adicionales ---
        for nombre, desc, precio in [
            ('Desayuno', 'Desayuno típico guajiro por persona.', '18000'),
            ('Lavandería', 'Lavado y planchado por prenda.', '8000'),
            ('Tour Cabo de la Vela', 'Transporte y guía por día.', '250000'),
            ('Transporte aeropuerto', 'Traslado desde o hacia el aeropuerto.', '40000'),
        ]:
            Servicio.objects.get_or_create(
                alojamiento=posada, nombre=nombre,
                defaults={'descripcion': desc, 'precio': precio},
            )


        # --- Usuarios de prueba (uno por rol) ---
        usuarios = [
            ('recepcion', 'Recepcionista', Rol.RECEPCIONISTA),
            ('gerente', 'Gerente', Rol.GERENTE),
            ('cliente', 'Cliente', Rol.CLIENTE),
        ]
        for username, nombre, rol in usuarios:
            if not Usuario.objects.filter(username=username).exists():
                Usuario.objects.create_user(
                    username=username, email=f'{username}@syshsena.co', password='Syshsena2026*',
                    first_name=nombre, last_name='Prueba',
                    rol=Rol.objects.get(nombre=rol),
                )

        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados correctamente.'))