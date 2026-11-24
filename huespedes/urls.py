from django.urls import path

from .views import HuespedesView

urlpatterns = [
    path('huespedes/', HuespedesView.as_view(), name='huespedes'),
]
