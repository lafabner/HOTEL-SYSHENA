from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('', include('reservas.urls')),
    path('', include('huespedes.urls')),
    path('', include('operaciones.urls')),
    path('', include('pagos.urls')),
    path('', include('habitaciones.urls')),
    path('', include('reservas.urls')),
    path('', include('huespedes.urls')),
    path('', include('operaciones.urls')),
    path('', include('pagos.urls')),
    path('', include('habitaciones.urls')),
    path('', include('reportes.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
