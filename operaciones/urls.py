from django.urls import path

from .views import OperacionView

urlpatterns = [
    path('operacion/', OperacionView.as_view(), name='operacion'),
]
