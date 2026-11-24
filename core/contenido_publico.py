"""Textos editoriales de la portada, sin modificar registros de la base de datos.

No añadas estrellas, fechas de fundación, amenidades o certificaciones sin validar.
La descripción/contactos/precios de la base de datos siguen siendo prioritarios.
"""
PRESENTACION = {
    'titulo': 'Una estancia cercana. Un destino por descubrir.',
    'descripcion': (
        'Guajira Serena es una propuesta de alojamiento para quienes buscan hacer '
        'una pausa y organizar su visita a La Guajira con tranquilidad. Reunimos '
        'habitaciones, servicios adicionales e información del destino en un mismo '
        'lugar, para que puedas elegir tu estancia con mayor claridad.'
    ),
    'proposito': (
        'Nuestra propuesta es acompañarte desde la elección de tu habitación hasta '
        'la consulta de tu reserva. Queremos que encuentres información comprensible '
        'sobre opciones, precios y horarios, y un contacto directo con el alojamiento '
        'cuando necesites confirmar algún detalle.'
    ),
}

DESCRIPCIONES_HABITACION = {
    'sencilla': 'Una alternativa para viajar por tu cuenta y tener tu propio espacio de descanso. Revisa la capacidad y las fechas antes de reservar.',
    'doble': 'Una opción para compartir la estancia. Consulta la capacidad disponible y confirma con el alojamiento la distribución de camas que necesitas.',
    'familiar': 'Pensada para quienes organizan un viaje en familia o en grupo. Elige según el número de personas y verifica la capacidad máxima publicada.',
}

DESCRIPCIONES_SERVICIO = {
    'desayuno': 'Organiza la primera comida del día sin dejarla para el último momento. Consulta con recepción horarios, opciones y necesidades alimentarias antes de solicitarlo.',
    'lavanderia': 'Una alternativa útil para estancias de varios días. Confirma con recepción qué prendas se reciben, los tiempos de entrega y la unidad de cobro.',
    'transporte': 'Planea tu llegada o salida con anticipación. Confirma el recorrido, los horarios y el valor aplicable antes de solicitar el traslado.',
    'tour': 'Descubre opciones para recorrer la región. Pide información sobre itinerario, duración, disponibilidad, inclusiones y condiciones antes de contratar.',
    'recorrido': 'Descubre opciones para recorrer la región. Pide información sobre itinerario, duración, disponibilidad, inclusiones y condiciones antes de contratar.',
}

# El video incluido es una animación de una imagen de IA, no una grabación del hotel.
# Puedes cambiar archivo/poster por archivos propios manteniendo rutas válidas.
HERO_MEDIA = [
    {'tipo': 'video', 'archivo': 'video/bienvenida.mp4', 'poster': 'img/alojamiento.jpg',
     'etiqueta': 'BIENVENIDO A GUAJIRA SERENA', 'titulo': 'Haz una pausa.\nDescubre La Guajira.',
     'texto': 'Tu próxima estancia empieza con un lugar para descansar y un destino por descubrir.',
     'accion': 'Conoce nuestra propuesta', 'ancla': '#nosotros',
     'nota': 'Video animado de una imagen de IA. No es una grabación real.'},
    {'tipo': 'imagen', 'archivo': 'img/habitacion-doble.jpg', 'poster': '',
     'etiqueta': 'TU ESPACIO PARA DESCANSAR', 'titulo': 'Elige cómo quieres\nvivir tu estancia.',
     'texto': 'Conoce los tipos de habitación, su capacidad y la tarifa por noche.',
     'accion': 'Explora las habitaciones', 'ancla': '#habitaciones',
     'nota': 'Imagen ilustrativa generada con IA.'},
    {'tipo': 'imagen', 'archivo': 'img/sitios/paisaje-guajira.jpg', 'poster': '',
     'etiqueta': 'UN DESTINO QUE INVITA A EXPLORAR', 'titulo': 'Más allá\ndel alojamiento.',
     'texto': 'Inspírate con la región y consulta las opciones de visita registradas por el alojamiento.',
     'accion': 'Descubre el destino', 'ancla': '#destinos',
     'nota': 'Paisaje ilustrativo generado con IA; no documenta un sitio concreto.'},
    {'tipo': 'imagen', 'archivo': 'img/habitacion-familiar.jpg', 'poster': '',
     'etiqueta': 'PLANEA EL VIAJE A TU MANERA', 'titulo': 'Comparte el viaje.\nEncuentra tu espacio.',
     'texto': 'Consulta fechas y capacidad para organizar tu próxima visita con compañía.',
     'accion': 'Planea tu estancia', 'ancla': '#buscar-estancia',
     'nota': 'Imagen ilustrativa generada con IA.'},
]
