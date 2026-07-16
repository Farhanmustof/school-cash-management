
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('students/', views.StudentAPIView.as_view(), name='api-students'),
    path('payments/', views.PaymentAPIView.as_view(), name='api-payments'),
    path('dashboard/', views.DashboardAPIView.as_view(), name='api-dashboard'),
]