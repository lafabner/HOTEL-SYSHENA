from django.urls import path

from .views import DisponibilidadView, HabitacionesView

urlpatterns = [
    path('disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
    path('habitaciones/', HabitacionesView.as_view(), name='habitaciones'),
]
