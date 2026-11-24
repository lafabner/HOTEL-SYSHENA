from django.urls import path

from .views import MisReservasView, NuevaReservaView, ReservasView

urlpatterns = [
    path('reservas/', ReservasView.as_view(), name='reservas'),
    path('reservas/nueva/', NuevaReservaView.as_view(), name='nueva_reserva'),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
]
