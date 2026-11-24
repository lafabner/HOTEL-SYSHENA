def clase_estado_habitacion(estado):
    """Clase CSS de la etiqueta de estado, igual que en Disponibilidad."""
    return {
        'DISPONIBLE': 'available',
        'OCUPADA': 'occupied',
        'MANTENIMIENTO': 'pending',
    }.get(estado, 'available')
