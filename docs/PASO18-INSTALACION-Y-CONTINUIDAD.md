# SysHSENA: paso 18

Paquete incremental sobre los pasos 15, 16 y 17. Completa la galería turística, conecta las fotografías internas, añade favicon y recuperación de contraseña, renueva la portada y prepara un perfil de producción separado. No sustituye `config/settings.py`, no contiene una base de datos ni cambia usuarios o contraseñas.

## Instalar en Windows

### A. Copiar

Detén `runserver` con `Ctrl+C`. Haz una copia de la carpeta del proyecto, extrae el ZIP y copia su contenido sobre `C:\laragon\www\syshsena`, aceptando reemplazar archivos. No borres tus carpetas `media`, migraciones ni configuración local.

### B. Activar y comprobar

```powershell
cd C:\laragon\www\syshsena
python instalar_paso18.py
python manage.py check
python manage.py test tests_paso18 --settings=config.settings_test -v 2
python manage.py runserver
```

El instalador hace un respaldo de tu `settings.py` antes de añadir una única importación. Conserva tus parámetros MySQL y no crea cuentas. Es idempotente: ejecutarlo de nuevo no duplica el cambio.

No hay cambios de modelos, por lo que este paso no requiere `makemigrations` ni `migrate`. La suite usa SQLite en memoria y no opera sobre tu base de datos MySQL. Sí requiere que los modelos y migraciones de los pasos anteriores estén instalados.

### C. Abrir

Con el servidor de Django del comando anterior, abre **http://127.0.0.1:8000/**. La ruta de Windows `C:\laragon\www\syshsena` no convierte automáticamente la dirección de Django en `http://localhost/syshsena/`; esa dirección solo aplica si configuraste expresamente un proxy de Laragon.

Pulsa `Ctrl+F5` si sigues viendo el diseño anterior. Prueba portada, login, Habitaciones, Disponibilidad y Recuperar contraseña.

## Cambios funcionales y visuales

- **Portada:** fotografía amplia, tipografía editorial Boska combinada con Satoshi, paleta arena/verde costero, formulario de fechas y huéspedes, tarjetas con precios COP, servicios, destinos y contacto.
- **Móvil:** menú desplegable accesible, controles de fecha adaptados, Escape para cerrar menú y composición a una columna. Revisado a 375 px y 1440 px sin desbordamiento horizontal.
- **Búsqueda:** envía fechas y huéspedes a la consulta de disponibilidad existente. Si no hay sesión, Django solicita acceso y conserva la URL de destino mediante `next`; no se implementó una consulta anónima de inventario independiente.
- **Portada con sesión:** ya puedes visitar `/` sin ser expulsado al panel. El enlace Mi panel vuelve al panel del rol. El login conserva la redirección por rol y respeta destinos `next` locales.
- **Reservas del cliente:** corregido el retorno al guardar: ahora vuelve a Mis reservas, no a una tabla administrativa que el cliente no puede abrir.
- **Registro:** creación de usuario y huésped dentro de una transacción, para no dejar una cuenta incompleta si falla la segunda operación.
- **Imágenes internas:** Habitaciones y Disponibilidad usan la misma función de selección que la portada y exponen `data-habitacion`. Ya no quedan los recuadros vacíos que mostraba la captura.
- **Favicon:** reutiliza el símbolo de ondas y sol del sistema. Incluido en panel, login y base pública.
- **Contenido comercial:** retiradas las promesas no configuradas de atención 24 h y respuesta en 24 h. No se añadieron reseñas, estrellas ni amenidades inventadas.

## Galería de sitios turísticos

La portada recorre los `SitioTuristico` activos del alojamiento activo. Muestra nombre, descripción, distancia si está registrada e imagen; si no hay sitios, muestra un estado vacío explícito, sin inventar registros.

Para registrar destinos usa el admin de Django:

1. Abre `http://127.0.0.1:8000/admin/`.
2. Entra como superusuario; el rol Administrador por sí solo no concede automáticamente acceso al admin de Django.
3. Abre Alojamientos, selecciona el alojamiento y completa las filas de Sitios turísticos.
4. Para una fotografía específica coloca un JPEG en `public/img/sitios/<nombre-en-slug>.jpg`. Ejemplo de convención: `Cabo de la Vela` se resuelve como `cabo-de-la-vela.jpg`.

Si no existe ese archivo se usa `public/img/sitios/paisaje-guajira.jpg`, una ilustración generada para esta entrega. La imagen representa un paisaje genérico inspirado en la región, no documenta el aspecto real de un sitio concreto. El texto de la interfaz lo aclara.

## Fotografías del hotel y las habitaciones

### Archivos incluidos

| Archivo | Uso |
| --- | --- |
| `public/img/alojamiento.jpg` | Portada ilustrativa mientras no haya foto real registrada |
| `public/img/habitacion-sencilla.jpg` | Tipos sencillos y respaldo para tipos no reconocidos |
| `public/img/habitacion-doble.jpg` | Tipos doble, matrimonial y suite |
| `public/img/habitacion-familiar.jpg` | Tipos familiares |
| `public/img/sitios/paisaje-guajira.jpg` | Respaldo ilustrativo de galería turística |
| `public/img/favicon.svg` | Icono de pestaña |

Las cuatro primeras imágenes son las generadas en el paso 17; no son fotos reales del hotel. La correspondencia por tipo está centralizada en `core/templatetags/imagenes.py`. Asignar el respaldo de Doble a una Suite no afirma que sea una fotografía de esa Suite.

### Activar una foto real del alojamiento

El modelo `FotoAlojamiento` ya existía. En el admin, abre el alojamiento, añade la fotografía en la sección de Fotos, escribe un texto alternativo real, marca Principal y guarda. La portada ahora da prioridad a esa foto y usa `imagen.url`, por lo que deja de mostrar la imagen generada.

No se recibieron fotos reales para esta entrega: no se reemplazaron ni se inventó su procedencia. Para habitaciones puedes sustituir los JPEG manteniendo nombres; las etiquetas conservadoras de “imagen ilustrativa” seguirán visibles hasta verificar y actualizar el material. Aún no existe un gestor de fotografías por habitación o sitio turístico en la interfaz propia; hotel sí dispone del modelo y admin citados.

## Recuperar contraseña

Se incorporó el circuito completo de Django:

| Ruta | Función |
| --- | --- |
| `/recuperar-contrasena/` | Solicitar instrucciones |
| `/recuperar-contrasena/enviado/` | Confirmación genérica |
| `/restablecer/<uid>/<token>/` | Validar enlace y elegir contraseña |
| `/restablecer/completado/` | Confirmación final |

El enlace vence en una hora. El cambio invalida el token y aplica las validaciones de contraseña configuradas en Django. Una dirección desconocida recibe la misma pantalla de confirmación, sin revelar si existe la cuenta; esto no implica una garantía de resistencia a análisis de tiempos.

### Prueba local sin servicio de correo

Sin `EMAIL_HOST`, el backend imprime el mensaje en la terminal de `runserver`. Solicita recuperación con el correo de una cuenta activa, copia el enlace que aparezca en PowerShell, ábrelo y elige la contraseña nueva. Si la cuenta no existe, está inactiva o no tiene contraseña utilizable, no se genera un mensaje.

Esto no envía un correo real. En esta entrega solo se probaron correo en memoria y consola, no un proveedor SMTP externo.

### Configurar SMTP

Configura las variables del proveedor real en la misma terminal o en el gestor seguro del servidor. No escribas claves dentro del código, en el ZIP ni en el chat.

```powershell
$env:EMAIL_HOST = "SERVIDOR-SMTP-REAL"
$env:EMAIL_PORT = "587"
$env:EMAIL_HOST_USER = "CUENTA-DEL-PROVEEDOR"
$env:EMAIL_USE_TLS = "true"
$env:EMAIL_USE_SSL = "false"
$env:DEFAULT_FROM_EMAIL = "REMITENTE-AUTORIZADO"
```

Define `EMAIL_HOST_PASSWORD` mediante el gestor de secretos de tu equipo/hosting antes de ejecutar el servidor. Si el proveedor exige SSL directo, configura su puerto, `EMAIL_USE_SSL=true` y `EMAIL_USE_TLS=false`; no actives ambos. El archivo `runtime.py` lee variables del entorno, no carga automáticamente archivos `.env`.

## Producción: preparada, no publicada

Se entregan `settings_production.py`, `wsgi_production.py` y `requirements-production.txt`. No se cambió tu desarrollo a `DEBUG=False` ni se sustituyó tu `SECRET_KEY` local. El perfil de producción exige una clave nueva y dominios explícitos, activa cookies seguras y redirección HTTPS, configura WhiteNoise y requiere SMTP.

Faltan el dominio real, el servidor de destino, certificado TLS, correo y fotos reales. Por tanto, **el hotel no está publicado en producción**.

### Comandos preparatorios

```powershell
python -m pip install -r requirements-production.txt

# Genera una clave distinta solo para producción, sin imprimirla:
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Sustituye por dominios realmente controlados, sin https:// ni rutas:
$env:DJANGO_ALLOWED_HOSTS = "DOMINIO-REAL,www.DOMINIO-REAL"
```

Configura también SMTP como se explica arriba. Asegura que la configuración de base de datos importada por `settings_production.py` apunte a la base MySQL de producción correcta, con un usuario dedicado y copias de seguridad; el complemento conserva tu `DATABASES`, no migra ni aprovisiona servidores.

```powershell
python manage.py check --deploy --settings=config.settings_production
python manage.py collectstatic --noinput --settings=config.settings_production
waitress-serve --listen=127.0.0.1:8000 config.wsgi_production:application
```

Waitress escucha solo en la interfaz local. Debe haber un proxy HTTPS (IIS, Apache o Nginx) delante; `runserver` no es el servidor de producción. Mantén Waitress como servicio supervisado, no como terminal que se cierra.

Si tu proxy fija `X-Forwarded-Proto` y elimina el valor enviado por clientes externos, puedes definir `DJANGO_TRUST_PROXY=true`. No actives esa confianza sin controlar el proxy. Configura `/media/` como contenido estático de solo lectura, deshabilita ejecución de archivos y listado de directorios. WhiteNoise sirve `staticfiles`, no los archivos subidos en `media`.

`check --deploy` conserva dos avisos HSTS: subdominios y preload. Se dejaron sin activar porque aún no se conocen los dominios y certificados; no se deben activar a ciegas. HSTS inicial de una hora para un despliegue gradual.

### Comprobaciones previas a abrirlo al público

- Migrar las acciones antiguas que modifican datos mediante GET a formularios POST con CSRF. No se hizo una reescritura completa de esos módulos en esta entrega.
- Limitar intentos de login y recuperación en el proxy o mediante una solución persistente.
- Confirmar protección de datos personales, recuperación de respaldos, transporte HTTPS y permisos del usuario MySQL.
- Cambiar contraseñas de demostración y desactivar cuentas no usadas.
- Configurar SMTP real, límites, registro de errores y monitorización.

Estos puntos son condiciones de endurecimiento antes de un lanzamiento público, no tareas completadas por haber creado un archivo de settings.

## Pruebas ejecutadas

Se añadieron **22 tests Django** en `tests_paso18/test_sistema.py` y todos pasaron en el sandbox con SQLite aislado:

- Portada, destinos, estado vacío, favicon, resolución de imágenes y prioridad de foto real.
- Registro, rechazo de documento/teléfono inválidos y correo duplicado, reversión atómica.
- Login por correo y redirecciones por rol, restricciones del cliente y carga de diez pantallas administrativas.
- Imágenes de Habitaciones y Disponibilidad.
- Reserva del cliente, prevención secuencial de solapamientos, pago excesivo y ciclo check-in/pago/check-out.
- Solicitud para dirección desconocida, recuperación completa, token vencido y token no reutilizable.

No es una prueba de concurrencia real de MySQL, ni una auditoría integral de seguridad o de rendimiento.

Además se revisó con Chromium: portada a 1440 y 375 px, menú móvil abierto/cerrado, ausencia de desbordamiento, imágenes turísticas cargadas, bloqueo de letras al teclear documentos y carga de las pantallas principales. No se observaron errores JavaScript en los recorridos realizados.

Se probó `collectstatic` con el perfil de producción y variables de prueba no públicas. Se corrigieron dos referencias inexistentes a source maps de Bootstrap que impedían completar ese comando. El favicon respondió HTTP 200 desde WhiteNoise con `DEBUG=False`. No se realizó envío SMTP ni despliegue en un dominio real.

## Inventario de archivos

| Grupo | Archivos |
| --- | --- |
| Portada | `templates/publico/base_publico.html`, `templates/publico/inicio.html`, `public/css/publico.css`, `public/js/publico.js`, `core/views.py` |
| Fotografías y formato | `core/templatetags/__init__.py`, `core/templatetags/imagenes.py`, `templates/habitaciones/habitaciones.html`, `templates/habitaciones/disponibilidad.html`, `public/img/*` |
| Favicon y acceso | `templates/inc/base.html`, `templates/login.html`, `public/img/favicon.svg` |
| Recuperación | `usuarios/urls.py`, `templates/registration/password_reset_*`, `config/runtime.py` |
| Correcciones de flujo | `usuarios/views.py`, `reservas/views.py` |
| Producción | `config/settings_production.py`, `config/wsgi_production.py`, `requirements-production.txt` |
| Instalación y QA | `instalar_paso18.py`, `config/settings_test.py`, `tests_paso18/*`, este documento |
| Bootstrap | `public/css/bootstrap.css`, `public/js/bootstrap.bundle.js`: retirada únicamente la referencia al `.map` faltante |

## Información de continuidad para otra IA

Trabajar sobre la instalación acumulada hasta paso 18, no reconstruir desde los modelos del sandbox ni copiar su SQLite sobre Laragon. La instalación real está en Windows con Django/MySQL y los ZIP contienen parches incrementales.

No sobrescribir `config/settings.py` con el del sandbox: conserva conexión MySQL y credenciales locales. No regenerar migraciones antiguas como si la base fuera nueva. El paso 18 no altera esquema.

El proyecto conserva roles ADMINISTRADOR, RECEPCIONISTA, CLIENTE y GERENTE. La existencia de cuentas de demostración en el ordenador del usuario no fue verificada en esta entrega. No inferir sus contraseñas a partir de los hashes ni repetir como confirmado un listado histórico.

Para listar cuentas reales sin modificarlas:

```powershell
python manage.py shell -c "from usuarios.models import Usuario; print(list(Usuario.objects.values_list('username','email','rol__nombre','is_active')))"
```

No se garantiza correspondencia completa con todos los documentos originales del proyecto mediante estas pruebas: la suite verifica los flujos expresamente listados. La auditoría requisito por requisito debe realizarse contra esos documentos si se solicita.

Prioridad siguiente: fotos reales aportadas por el usuario; dominio/hosting y correo; endurecimiento POST/CSRF y límites de intentos; revisión de privacidad y pruebas en MySQL; lanzamiento supervisado. Evitar presentar imágenes generadas como evidencia del hotel real.
