"""Instala exclusivamente la portada del paso 19, con copia previa de seguridad."""
import argparse
import shutil
from datetime import datetime
from pathlib import Path

ARCHIVOS = [
    'core/contenido_publico.py',
    'core/views.py',
    'templates/publico/base_publico.html',
    'templates/publico/inicio.html',
    'public/css/portada.css',
    'public/js/publico.js',
    'public/video/bienvenida.mp4',
    'tests_paso19/__init__.py',
    'tests_paso19/test_portada.py',
    'docs/PASO19-PORTADA-Y-CONTINUIDAD.md',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', required=True, help='Carpeta del proyecto que contiene manage.py')
    args = parser.parse_args()
    origen = Path(__file__).resolve().parent
    destino = Path(args.destino).resolve()
    if origen == destino:
        raise SystemExit('Extrae el ZIP en una carpeta temporal, distinta del proyecto.')
    if not (destino / 'manage.py').is_file():
        raise SystemExit('El destino no contiene manage.py. No se modificó ningún archivo.')
    for archivo in ARCHIVOS:
        if not (origen / archivo).is_file():
            raise SystemExit(f'Paquete incompleto: falta {archivo}. No se modificó el destino.')
    for archivo in ('public/img/alojamiento.jpg', 'public/img/habitacion-doble.jpg',
                    'public/img/habitacion-familiar.jpg', 'public/img/sitios/paisaje-guajira.jpg',
                    'core/templatetags/imagenes.py', 'config/settings_test.py'):
        if not (destino / archivo).is_file():
            raise SystemExit(f'Falta un archivo del paso 18: {archivo}. Instala primero ese paso.')
    backup = destino / 'backups' / ('paso19-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    # Primero se respaldan todos los archivos existentes; después empieza la copia.
    for archivo in ARCHIVOS:
        actual = destino / archivo
        if actual.is_file():
            respaldo = backup / archivo
            respaldo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(actual, respaldo)
    for archivo in ARCHIVOS:
        salida = destino / archivo
        salida.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen / archivo, salida)
        print('Instalado:', archivo)
    print('\nRespaldo de archivos anteriores:', backup)
    print('No se modificaron settings.py, MySQL, migraciones, usuarios ni fotografías existentes.')
    print('Reinicia Django y actualiza el navegador con Ctrl+F5.')


if __name__ == '__main__':
    main()
