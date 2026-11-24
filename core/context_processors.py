from django.urls import NoReverseMatch, reverse

from .navegacion import MENU


def navegacion(request):
    """Entrega a todas las plantillas el menú según el rol y los datos del usuario."""
    usuario = request.user
    if not usuario.is_authenticated:
        return {}
    rol = usuario.rol.nombre
    actual = getattr(request.resolver_match, 'url_name', None)
    secciones = {}
    for seccion, nombre, url, icono, roles in MENU:
        if rol not in roles:
            continue
        try:
            href = reverse(url)
        except NoReverseMatch:
            href = '#'
        secciones.setdefault(seccion, []).append(
            {'nombre': nombre, 'href': href, 'icono': icono, 'activo': url == actual})

    nombre_completo = usuario.get_full_name() or usuario.username
    partes = nombre_completo.split()
    iniciales = (partes[0][0] + partes[-1][0]) if len(partes) > 1 else nombre_completo[:2]
    return {
        'menu_secciones': secciones,
        'usuario_nombre': nombre_completo,
        'usuario_iniciales': iniciales.upper(),
        'usuario_rol': usuario.rol.get_nombre_display(),
    }
