from django.urls import path

from .views import PagosView

urlpatterns = [
    path('pagos/', PagosView.as_view(), name='pagos'),
]
