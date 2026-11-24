"""Cálculo de los indicadores del dashboard (CU-15).
Solo consulta datos: no modifica nada."""
from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from habitaciones.models import Habitacion
from huespedes.models import Huesped
from pagos.models import Pago
from reservas.models import Reserva

DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']


def formato_moneda(valor):
    """$18,4 M para millones; $850.000 para valores menores."""
    valor = Decimal(valor or 0)
    if valor >= 1_000_000:
        return '$' + f'{valor / 1_000_000:.1f}'.replace('.', ',') + ' M'
    return '$' + f'{valor:,.0f}'.replace(',', '.')


def _inicio_dia(fecha):
    return timezone.make_aware(datetime.combine(fecha, time.min))


def calcular_dashboard(hoy=None):
    hoy = hoy or timezone.localdate()

    # ---- Habitaciones ----
    activas = Habitacion.objects.filter(activa=True)
    total = activas.count()
    ocupadas = activas.filter(estado=Habitacion.OCUPADA).count()
    mantenimiento = activas.filter(estado=Habitacion.MANTENIMIENTO).count()
    disponibles = activas.filter(estado=Habitacion.DISPONIBLE).count()
    ocupacion = (Decimal(ocupadas) * 100 / total) if total else Decimal(0)

    # ---- Reservas ----
    activas_res = Reserva.objects.filter(
        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA]).count()
    llegadas = Reserva.objects.filter(
        fecha_entrada=hoy, estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA]).count()
    salidas = Reserva.objects.filter(
        fecha_salida=hoy, estado=Reserva.EN_ESTADIA).count()

    # ---- Ingresos del mes ----
    inicio_mes = hoy.replace(day=1)
    ingresos_mes = Pago.objects.filter(
        fecha_hora__gte=_inicio_dia(inicio_mes)).aggregate(t=Sum('valor'))['t'] or Decimal(0)

    # ---- Ingresos de los últimos 7 días (se agrupa en Python para no
    #      depender de las tablas de zona horaria de MySQL) ----
    dias = [hoy - timedelta(days=n) for n in range(6, -1, -1)]
    por_dia = {d: Decimal(0) for d in dias}
    pagos = Pago.objects.filter(fecha_hora__gte=_inicio_dia(dias[0])).values_list('fecha_hora', 'valor')
    for momento, valor in pagos:
        dia = timezone.localtime(momento).date()
        if dia in por_dia:
            por_dia[dia] += valor
    maximo = max(por_dia.values()) if por_dia else Decimal(0)
    barras = []
    for d in dias:
        valor = por_dia[d]
        altura = int(valor * 100 / maximo) if maximo else 0
        barras.append({
            'etiqueta': DIAS[d.weekday()],
            'valor': valor,
            'texto': formato_moneda(valor),
            'altura': max(altura, 3) if valor else 0,
            'hoy': d == hoy,
        })

    # ---- Dona de estado de habitaciones (porcentajes acumulados) ----
    def pct(n):
        return (n * 100 / total) if total else 0
    p_ocup = pct(ocupadas)
    p_mant = pct(ocupadas + mantenimiento)

    recientes = (Reserva.objects.select_related('huesped', 'habitacion')
                 .order_by('-creado_en', '-id')[:6])

    return {
        'hoy': hoy,
        'hab_total': total,
        'hab_disponibles': disponibles,
        'hab_ocupadas': ocupadas,
        'hab_mantenimiento': mantenimiento,
        'ocupacion': f'{ocupacion:.1f}'.replace('.', ','),
        'ocupacion_entera': round(ocupacion),
        'reservas_activas': activas_res,
        'reservas_dia': llegadas + salidas,
        'llegadas': llegadas,
        'salidas': salidas,
        'huespedes': Huesped.objects.count(),
        'ingresos_mes': formato_moneda(ingresos_mes),
        'ingresos_7_dias': formato_moneda(sum(por_dia.values())),
        'barras': barras,
        'dona_ocupadas': f'{p_ocup:.2f}',
        'dona_mantenimiento': f'{p_mant:.2f}',
        'recientes': recientes,
    }


def calcular_reportes(desde, hasta):
    """Reportes del periodo (CU-15): ingresos, reservas, ocupación y servicios."""
    from decimal import Decimal
    from datetime import time, datetime

    from django.db.models import Count, Sum

    from habitaciones.models import Habitacion
    from huespedes.models import Huesped
    from pagos.models import Pago
    from reservas.models import Reserva
    from servicios.models import ServicioReserva

    inicio = timezone.make_aware(datetime.combine(desde, time.min))
    fin = timezone.make_aware(datetime.combine(hasta, time.max))

    pagos = Pago.objects.filter(fecha_hora__range=(inicio, fin))
    total_recaudado = pagos.aggregate(t=Sum('valor'))['t'] or Decimal('0')
    n_pagos = pagos.count()

    reservas_periodo = Reserva.objects.filter(creado_en__range=(inicio, fin))
    n_reservas = reservas_periodo.count()
    activas = Reserva.objects.filter(
        estado__in=Reserva.ESTADOS_BLOQUEANTES,
        fecha_entrada__lte=hasta, fecha_salida__gte=desde)
    saldos = activas.aggregate(t=Sum('saldo_pendiente'))['t'] or Decimal('0')

    total_hab = Habitacion.objects.filter(activa=True).count()
    ocupadas = (Habitacion.objects.filter(activa=True, estado=Habitacion.OCUPADA).count())
    ocupacion = (Decimal(ocupadas) * 100 / total_hab) if total_hab else Decimal('0')

    consumos = (ServicioReserva.objects
                .filter(fecha_hora__range=(inicio, fin))
                .values('servicio__nombre')
                .annotate(cantidad=Sum('cantidad'), total=Sum('subtotal'))
                .order_by('-total'))

    # Ingresos por semana del periodo
    semanas = {}
    for pago in pagos:
        dia = timezone.localtime(pago.fecha_hora).date()
        semana = dia.isocalendar()[1]
        semanas.setdefault(semana, Decimal('0'))
        semanas[semana] += pago.valor
    maximo = max(semanas.values()) if semanas else Decimal('0')
    barras = []
    for i, (semana, valor) in enumerate(sorted(semanas.items()), start=1):
        altura = int(valor * 100 / maximo) if maximo else 0
        barras.append({'etiqueta': f'Sem {i}', 'valor': valor,
                       'texto': formato_moneda(valor),
                       'altura': max(altura, 3) if valor else 0})

    return {
        'total_recaudado': formato_moneda(total_recaudado),
        'n_pagos': n_pagos,
        'saldos_pendientes': formato_moneda(saldos),
        'ocupacion_media': f'{ocupacion:.1f}'.replace('.', ','),
        'n_reservas': n_reservas,
        'n_huespedes': Huesped.objects.count(),
        'barras': barras,
        'servicios_vendidos': [
            {'nombre': c['servicio__nombre'], 'cantidad': c['cantidad'],
             'total': formato_moneda(c['total'])} for c in consumos],
    }
