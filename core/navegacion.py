"""Definición única del menú lateral y de qué rol ve cada opción.
Coincide con la matriz de navegación por rol del documento de diseño."""
from usuarios.models import Rol

A = Rol.ADMINISTRADOR
R = Rol.RECEPCIONISTA
C = Rol.CLIENTE
G = Rol.GERENTE

# (sección, nombre visible, nombre de la URL, icono, roles que la ven)
MENU = [
    ('Operación', 'Dashboard', 'dashboard', '◫', (A, G)),
    ('Operación', 'Disponibilidad', 'disponibilidad', '⌕', (A, R, C, G)),
    ('Operación', 'Reservas', 'reservas', '▣', (A, R, G)),
    ('Operación', 'Mis reservas', 'mis_reservas', '▣', (C,)),
    ('Operación', 'Nueva reserva', 'nueva_reserva', '＋', (A, R, C)),
    ('Operación', 'Check-in / Check-out', 'operacion', '⇄', (A, R, G)),
    ('Administración', 'Habitaciones', 'habitaciones', '▤', (A, R, C, G)),
    ('Administración', 'Huéspedes', 'huespedes', '♙', (A, R, G)),
    ('Administración', 'Pagos y servicios', 'pagos', '$', (A, R, G)),
    ('Administración', 'Reportes', 'reportes', '▥', (A, G)),
    ('Administración', 'Usuarios y roles', 'usuarios', '☷', (A,)),
    ('Administración', 'Configuración', 'configuracion', '⚙', (A,)),
]

ROLES_POR_URL = {url: roles for _, _, url, _, roles in MENU}
NOMBRE_POR_URL = {url: nombre for _, nombre, url, _, _ in MENU}

# Pantalla a la que se envía a cada rol después de iniciar sesión
INICIO_POR_ROL = {A: 'dashboard', G: 'dashboard', R: 'reservas', C: 'mis_reservas'}
