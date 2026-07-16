from django.urls import path
from . import views

# Pastikan app_name sudah benar
app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    # Pastikan baris di bawah ini ada dan namanya 'payment_report'
    path('pembayaran/', views.PaymentReportView.as_view(), name='payment_report'),
    path('export-pdf/', views.ExportPaymentPDFView.as_view(), name='export_pdf'),
]