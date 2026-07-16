from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Daftar Siswa & Tambah Siswa
    path('', views.StudentListView.as_view(), name='list'),
    path('create/', views.StudentCreateView.as_view(), name='create'),
    
    # Detail, QR, Edit, dan Hapus (Semua menggunakan UUID)
    path('<uuid:pk>/', views.StudentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.StudentUpdateView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.StudentDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/qr/', views.StudentQRView.as_view(), name='qr'),
    
    # Export Data
    path('export/excel/', views.StudentExportExcelView.as_view(), name='export_excel'),
]