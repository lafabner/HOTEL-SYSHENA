"""Configuración independiente de producción. Requiere HTTPS delante de Waitress."""
from .settings import *  # noqa: F403
from .runtime import *  # noqa: F403
import os
from django.core.exceptions import ImproperlyConfigured


def obligatorio(nombre):
    valor = os.environ.get(nombre, '').strip()
    if not valor:
        raise ImproperlyConfigured(f'Falta la variable {nombre} para producción.')
    return valor


DEBUG = False
SECRET_KEY = obligatorio('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('DJANGO_SECRET_KEY debe ser aleatoria, de al menos 50 caracteres.')
ALLOWED_HOSTS = [h.strip() for h in obligatorio('DJANGO_ALLOWED_HOSTS').split(',') if h.strip()]
if '*' in ALLOWED_HOSTS or any('://' in h or '/' in h for h in ALLOWED_HOSTS):
    raise ImproperlyConfigured('Indica dominios explícitos, sin protocolo, ruta ni comodines.')
CSRF_TRUSTED_ORIGINS = [f'https://{h}' for h in ALLOWED_HOSTS]
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
X_FRAME_OPTIONS = 'DENY'
# Activa solo si el proxy elimina cabeceras recibidas del público y fija la suya.
if os.environ.get('DJANGO_TRUST_PROXY') == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not EMAIL_HOST or DEFAULT_FROM_EMAIL.endswith('@localhost'):  # noqa: F405
    raise ImproperlyConfigured('Configura SMTP y DEFAULT_FROM_EMAIL antes de publicar.')
