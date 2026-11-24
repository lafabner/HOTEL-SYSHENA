from django.urls import path

from .views import DashboardView, ReportesView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
]
