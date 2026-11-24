from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.errores import ErrorNegocio
from habitaciones.models import Habitacion
from huespedes.models import Huesped
from operaciones.logica import realizar_checkin, realizar_checkout
from pagos.logica import registrar_pago
from reservas import logica as rl
from reservas.models import Reserva, SolicitudCancelacion
from servicios.logica import registrar_consumo
from servicios.models import Servicio
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Prueba la lógica de negocio y revierte todos los cambios.'

    def ok(self, texto, condicion):
        if not condicion:
            self.fallos += 1
        print(('  [OK]    ' if condicion else '  [FALLO] ') + texto)

    def error(self, texto, funcion):
        try:
            funcion()
        except ErrorNegocio as e:
            print(f'  [OK]    {texto} -> "{e}"')
        else:
            self.fallos += 1
            print(f'  [FALLO] {texto} -> no lanzó error')

    def handle(self, *args, **options):
        self.fallos = 0
        with transaction.atomic():
            self.recorrido()
            transaction.set_rollback(True)
        print()
        if self.fallos:
            self.stdout.write(self.style.ERROR(f'{self.fallos} prueba(s) fallaron.'))
        else:
            self.stdout.write(self.style.SUCCESS('Todas las pruebas pasaron. (Cambios revertidos)'))

    def recorrido(self):
        admin = Usuario.objects.filter(is_superuser=True).first()
        cliente = Usuario.objects.get(username='cliente')
        huesped = Huesped.objects.first()
        huesped.usuario = cliente
        huesped.save()
        hab = Habitacion.objects.get(numero='202')
        desayuno = Servicio.objects.get(nombre='Desayuno')
        hoy = timezone.localdate()
        d = lambda n: hoy + timedelta(days=30 + n)

        print('1. Disponibilidad y creación')
        self.ok('202 aparece disponible para 4 huéspedes',
                hab in rl.habitaciones_disponibles(d(0), d(3), 4))
        r1 = rl.crear_reserva(huesped=huesped, habitacion=hab, fecha_entrada=d(0),
                              fecha_salida=d(3), numero_huespedes=3, creada_por=admin)
        self.ok(f'Reserva creada con código {r1.codigo}', r1.codigo.startswith('RES-'))
        self.ok('Total = 3 noches x 220.000 = 660.000', r1.valor_total == 660000)
        self.ok('202 ya no aparece disponible en esas fechas',
                hab not in rl.habitaciones_disponibles(d(0), d(3), 4))

        print('2. Reglas de reserva')
        self.error('Cruce de fechas', lambda: rl.crear_reserva(
            huesped=huesped, habitacion=hab, fecha_entrada=d(2), fecha_salida=d(5),
            numero_huespedes=2, creada_por=admin))
        self.error('Capacidad excedida (6 en capacidad 4)', lambda: rl.crear_reserva(
            huesped=huesped, habitacion=hab, fecha_entrada=d(10), fecha_salida=d(12),
            numero_huespedes=6, creada_por=admin))
        self.error('Salida anterior a entrada', lambda: rl.crear_reserva(
            huesped=huesped, habitacion=hab, fecha_entrada=d(12), fecha_salida=d(10),
            numero_huespedes=2, creada_por=admin))
        r2 = rl.crear_reserva(huesped=huesped, habitacion=hab, fecha_entrada=d(3),
                              fecha_salida=d(5), numero_huespedes=2, creada_por=admin)
        self.ok('Salida de una reserva = entrada de otra es válido', r2.pk is not None)

        print('3. Check-in, consumos y pagos')
        realizar_checkin(r1, admin, 'Llegada sin novedad')
        r1.refresh_from_db(); hab.refresh_from_db()
        self.ok('Reserva EN_ESTADIA y habitación OCUPADA',
                r1.estado == Reserva.EN_ESTADIA and hab.estado == Habitacion.OCUPADA)
        self.error('Segundo check-in', lambda: realizar_checkin(r1, admin))
        registrar_consumo(r1, desayuno, 2, admin)
        r1.refresh_from_db()
        self.ok('Desayuno x2 (36.000) -> total 696.000', r1.valor_total == 696000)
        self.error('Pago mayor al saldo', lambda: registrar_pago(r1, 700000, 'EFECTIVO', admin))
        self.error('Pago en cero', lambda: registrar_pago(r1, 0, 'EFECTIVO', admin))
        registrar_pago(r1, 300000, 'TRANSFERENCIA', admin, referencia='TRX-001')
        r1.refresh_from_db()
        self.ok('Pago de 300.000 -> saldo 396.000', r1.saldo_pendiente == 396000)

        print('4. Check-out')
        self.error('Check-out con saldo pendiente', lambda: realizar_checkout(r1, admin))
        registrar_pago(r1, 396000, 'EFECTIVO', admin)
        realizar_checkout(r1, admin, 'Salida sin novedad')
        r1.refresh_from_db(); hab.refresh_from_db()
        self.ok('Reserva FINALIZADA y habitación DISPONIBLE',
                r1.estado == Reserva.FINALIZADA and hab.estado == Habitacion.DISPONIBLE)
        self.ok('Saldo en cero', r1.saldo_pendiente == 0)
        self.error('Registrar consumo en reserva finalizada',
                   lambda: registrar_consumo(r1, desayuno, 1, admin))

        print('5. Cancelación')
        sol = rl.solicitar_cancelacion(r2, cliente, 'Cambio de planes')
        self.ok('Solicitud pendiente creada', sol.estado == SolicitudCancelacion.PENDIENTE)
        self.error('Solicitud duplicada', lambda: rl.solicitar_cancelacion(r2, cliente, 'Otra vez'))
        rl.resolver_solicitud(sol, admin, aprobar=True, respuesta='Aprobada')
        r2.refresh_from_db()
        self.ok('Reserva CANCELADA tras aprobar', r2.estado == Reserva.CANCELADA)
        self.ok('Habitación libre otra vez en esas fechas',
                hab in rl.habitaciones_disponibles(d(3), d(5), 2))