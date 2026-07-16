
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('stats/', views.DashboardStatsAPI.as_view(), name='stats'),
    path('test-saldo/', views.DashboardView.as_view(), name='index'),
]