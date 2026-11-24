# SysHSENA: portada inmersiva y contenido para visitantes

Entrega incremental del paso 19, sobre el paso 18. Este cambio se concentra en la web pública del alojamiento y no altera la operación administrativa ni los datos existentes.

## Resultado

- **Apertura a pantalla completa:** cabecera transparente con marca central, menú a la izquierda y acceso a reservar a la derecha.
- **Carrusel vertical:** cuatro escenas con transiciones de arriba abajo: bienvenida animada, habitación doble, paisaje ilustrativo y habitación familiar. Una fotografía subida en FotoAlojamiento agrega una escena prioritaria al inicio.
- **Video:** archivo MP4 local, silencioso y en bucle, con una animación de acercamiento sobre la ilustración del alojamiento. Dura 10 segundos, mide 1280 × 720 y pesa aproximadamente 1,8 MB. No es una grabación real ni material tomado de Atlantis.
- **Navegación:** selectores, botones anterior/siguiente, flechas del teclado cuando el carrusel tiene foco y gesto vertical en pantalla táctil.
- **Más información:** presentación de la empresa, propuesta de atención, orientación para elegir, descripciones complementarias de habitaciones y servicios, pasos de reserva y preguntas frecuentes.
- **Continuidad:** la consulta de fechas y las rutas de registro, login, recuperación y contacto siguen utilizando Django.

La composición inicial toma como referencia la apertura audiovisual y la navegación discreta de [Atlantis, The Palm](https://www.atlantis.com/dubai/atlantis-the-palm), consultada el 28 de octubre de 2026. No se copiaron sus videos, fotografías, textos ni identidad corporativa.

## Alcance y datos que no se inventaron

La información editorial es una propuesta de redacción para el proyecto académico Guajira Serena. No afirma años de trayectoria, número de estrellas, certificaciones, premios, políticas de devolución, ubicación exacta de las ilustraciones ni equipamientos no verificados.

El nombre del alojamiento, descripción administrativa, habitaciones, capacidad, tarifas, servicios, destinos y datos de contacto continúan consultándose desde los modelos existentes. Las descripciones adicionales ayudan a interpretar esas opciones; no modifican los registros de la base de datos ni constituyen garantías de servicios.

La referencia a servicios en los textos depende de los servicios activos registrados: no se crea una lavandería, desayuno o transporte en la base de datos por añadir redacción. Cuando un nombre no coincide con los textos específicos, se muestra una orientación general para consultar condiciones.

## Archivos trabajados

| Archivo | Cambio |
|---|---|
| `core/contenido_publico.py` | Nuevo archivo editorial con presentación, textos de apoyo y configuración de las escenas. |
| `core/views.py` | Agrega contexto del carrusel y textos complementarios. Conserva los datos y redirecciones por rol existentes. |
| `templates/publico/base_publico.html` | Clase de portada por bloque, acceso Nosotros, botón Reservar y hoja de estilos nueva. Versionado del JS para evitar una copia antigua en caché. |
| `templates/publico/inicio.html` | Sustituye el hero estático por el carrusel y amplía las secciones públicas. |
| `public/css/portada.css` | Diseño inmersivo, contenido editorial, adaptación móvil, foco visible y movimiento reducido. |
| `public/js/publico.js` | Carrusel y control de reproducción; conserva el menú y la validación de fechas anteriores. |
| `public/video/bienvenida.mp4` | Nuevo video animado local, sin sonido. |
| `tests_paso19/test_portada.py` | Cinco pruebas nuevas de contenido, imágenes, datos y estados vacíos. |
| `tests_paso19/__init__.py` | Permite descubrir la suite nueva. |
| `instalar_paso19.py` | Instalador incremental con comprobaciones y respaldo de los archivos que reemplaza. |
| `docs/PASO19-PORTADA-Y-CONTINUIDAD.md` | Este informe de instalación y continuidad. |

No hay modelos nuevos, migraciones, dependencias nuevas ni cambios en `config/settings.py`. Los formularios internos no se modificaron en este paso.

## Imágenes y video: ubicación exacta

Se reutilizan las imágenes creadas en el paso 18. No se incluyen nuevamente en este ZIP para evitar sobrescribir fotografías que hayas sustituido por archivos reales.

| Recurso existente | Ubicación visible |
|---|---|
| `public/img/alojamiento.jpg` | Poster del video y fotografía de la sección Nosotros. También es la imagen utilizada para crear la animación actual. |
| `public/img/habitacion-doble.jpg` | Segunda escena del carrusel y tarjetas de tipo doble mediante el filtro existente. |
| `public/img/habitacion-familiar.jpg` | Cuarta escena y tarjetas de tipo familiar. |
| `public/img/habitacion-sencilla.jpg` | Tarjetas de habitaciones sencillas; conserva el comportamiento del paso 18. |
| `public/img/sitios/paisaje-guajira.jpg` | Tercera escena y respaldo visual de destinos sin imagen específica. |
| `public/video/bienvenida.mp4` | Primera escena animada del carrusel. |

Las ilustraciones mantienen avisos visibles. El paisaje no se presenta como fotografía documental de un lugar específico.

Para usar un video real, reemplaza `public/video/bienvenida.mp4` por un MP4 H.264 compatible con navegadores y actualiza su poster y el campo `nota` de la primera escena en `core/contenido_publico.py`. Es recomendable un clip horizontal de 8 a 15 segundos, sin información importante cerca de los bordes y con un peso contenido.

Reemplazar solamente `alojamiento.jpg` no cambia el contenido del MP4: la animación ya está codificada en el archivo de video. Si cambias la fotografía por una real, debes sustituir también el video o cambiar esa escena a `tipo: 'imagen'` y `archivo: 'img/alojamiento.jpg'`.

Para fotografías reales de habitaciones, conserva los nombres anteriores si representan correctamente los espacios, revisa el encuadre en móvil y retira los avisos de IA solamente en los componentes que realmente hayan pasado a utilizar fotografías reales. Las tarjetas del paso 18 también conservan sus propias etiquetas y deben actualizarse allí.

Una FotoAlojamiento registrada por administración tiene prioridad como primera escena y como imagen de Nosotros; no elimina las otras escenas ilustrativas. Si no deseas mostrarlas después de aportar fotografías reales, modifica `HERO_MEDIA`.

## Accesibilidad, rendimiento e interacción

- **Movimiento:** cambio automático cada nueve segundos, pausa/reproducción explícita y pausa al interactuar manualmente.
- **Preferencias:** si el sistema solicita movimiento reducido, no comienza la reproducción automática y se eliminan las transiciones.
- **Teclado:** flechas arriba/abajo dentro del carrusel, controles con nombre accesible y foco visible.
- **Escenas inactivas:** `aria-hidden` e `inert` impiden que sus enlaces entren en la navegación normal por teclado.
- **Lectores de pantalla:** un único h1 principal y anuncio de escena solo cuando la navegación es manual, para evitar anuncios automáticos constantes.
- **Video:** reproducción silenciada, `playsinline`, carga diferida hasta necesitarlo y poster como alternativa si falla la reproducción. No contiene diálogo ni audio que requiera subtítulos.
- **Consumo:** video y temporizador se suspenden cuando la pestaña está oculta o el carrusel queda fuera de vista.
- **Página normal:** no se intercepta la rueda del ratón ni se bloquea el desplazamiento de todo el documento.
- **Sin JavaScript:** queda visible la primera escena y los enlaces de contenido; el cambio de escena requiere JavaScript.
- **Móvil:** se comprobó a 375 × 812 y escritorio a 1440 × 1000, sin desbordamiento horizontal. Las etiquetas no bajan de 12 px.

## Validaciones y flujos conservados

No se cambiaron las reglas de documentos, teléfonos ni reservas del paso 18. Se verificó en navegador que escribir letras en documento y teléfono del registro deja únicamente los dígitos, y que cambiar la llegada sigue ajustando la fecha mínima de salida.

La búsqueda pública continúa enviando fechas y huéspedes a `disponibilidad`. Esa ruta requiere autenticación en la versión actual, por lo que un visitante anónimo es dirigido al login con su consulta en `next`; no se prometió disponibilidad pública anónima ni se alteró este requisito.

Las preguntas frecuentes explican cómo solicitar una cancelación sin inventar una política de devolución. Los precios adicionales muestran una indicación de confirmar la unidad de cobro con recepción.

## Verificación realizada

Comando de pruebas:

```powershell
python manage.py test tests_paso18 tests_paso19 --settings=config.settings_test
python manage.py check --settings=config.settings_test
```

Resultado en el entorno de trabajo: **27 pruebas aprobadas**, con base SQLite de prueba aislada y sin incidencias en el chequeo de Django. Las 22 pruebas previas se conservaron y se agregaron cinco para esta portada.

Las nuevas pruebas cubren portada sin alojamiento, contenido configurado, textos complementarios sin sobrescribir descripciones, prioridad de fotografía registrada y existencia de recursos estáticos.

La revisión en navegador cubrió navegación manual del carrusel, selector de escena, flechas, pausa/reproducción del MP4, menú de escritorio/móvil, enlaces a Nosotros/login, pregunta desplegable, consulta de fechas, registro numérico y recuperación. Se comprobó movimiento reducido sin reproducción automática y no se observaron errores JavaScript durante esos recorridos.

Las pruebas no equivalen a una auditoría de accesibilidad ni a ensayos de carga. El gesto táctil está implementado, pero conviene comprobarlo en un teléfono físico; los permisos de reproducción pueden variar entre navegadores.

## Instalación en Windows y Laragon

Requisito: proyecto funcionando con los cambios del paso 18. Guarda cualquier edición local propia antes de instalar; el respaldo permite comparar y recuperar archivos anteriores.

Detén el servidor Django. Descarga el ZIP y extrae el paquete en una carpeta temporal, no directamente sobre el proyecto:

```powershell
Expand-Archive -Path "$env:USERPROFILE\Downloads\paso19-syshsena.zip" -DestinationPath "$env:TEMP\syshsena-paso19" -Force
cd C:\laragon\www\syshsena
python "$env:TEMP\syshsena-paso19\instalar_paso19.py" --destino .
```

Usa el mismo entorno virtual y comando `python` con el que ejecutas actualmente SysHSENA. Si guardaste el ZIP en otra carpeta, ajusta la ruta.

El instalador valida los archivos necesarios del paso 18, respalda los archivos existentes en `backups/paso19-FECHA-HORA/` y copia únicamente los archivos enumerados. No modifica la conexión a MySQL, la clave de Django, usuarios, contraseñas ni fotografías existentes.

Después ejecuta las pruebas anteriores y reinicia:

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` y presiona Ctrl+F5. No necesitas ejecutar migraciones para este paso.

Para deshacer el cambio visual, detén Django y restaura los archivos respaldados a sus rutas originales. Los archivos nuevos que queden sin referencias no afectan los modelos ni la base de datos.

Si ya estás usando la configuración de producción, ejecuta también:

```powershell
python manage.py collectstatic --noinput --settings=config.settings_production
```

Esto requiere que tus variables de producción estén previamente configuradas; este paquete no contiene secretos ni modifica el dominio.

## Pendientes para continuar sin confusión

- **Contenido definitivo:** validar nombre comercial, descripción corporativa y estilo editorial con el responsable del hotel. Los textos propuestos están centralizados en `core/contenido_publico.py`.
- **Material real:** aportar fotos y un video propios con autorización de uso. Las imágenes actuales y la animación son ilustrativas.
- **Edición desde administración:** si se desea cambiar escenas o textos editoriales sin código, crear posteriormente un modelo y formulario específicos, con migraciones aditivas. Este paso no lo implementa.
- **Disponibilidad sin login:** definir si se desea abrir la consulta a anónimos, manteniendo autenticación para confirmar la reserva. El comportamiento actual se conservó.
- **Producción:** siguen pendientes dominio real, variables seguras, SMTP y despliegue operativo del paso 18. No se publicó el sistema del hotel en producción.
- **Seguridad heredada:** revisar las acciones que modifican estado mediante GET antes de exponer el sistema a Internet. Este paso visual no cambia esa parte de la aplicación.
- **Pruebas adicionales:** teléfono físico, Safari/iOS, lectura asistida, carga y mediciones de rendimiento con material real.
- **Credenciales:** no se crearon, cambiaron ni recuperaron contraseñas en este paso. No deducir credenciales de los usuarios de pruebas.

## Vista previa

La vista previa adjunta es una exportación visual de las páginas públicas con datos de demostración. El carrusel, navegación y contenido se pueden explorar; las operaciones de formulario se indican como demostración y no escriben en tu base de datos.

El ZIP contiene la implementación Django real para tu instalación. No se ha accedido a la base MySQL de tu computador ni se ha instalado automáticamente allí.
