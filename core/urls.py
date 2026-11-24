from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('configuracion/', views.ConfiguracionView.as_view(), name='configuracion'),
]
