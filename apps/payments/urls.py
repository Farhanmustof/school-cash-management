from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Halaman Utama Daftar Pembayaran
    path('', views.PaymentListView.as_view(), name='list'),
    
    # Halaman Input Pembayaran Baru
    path('create/', views.PaymentCreateView.as_view(), name='create'),
    
    # Halaman Detail Transaksi (Menggunakan UUID)
    path('<uuid:pk>/', views.PaymentDetailView.as_view(), name='detail'),
    
    # Fitur Konfirmasi/Tolak Pembayaran
    path('<uuid:pk>/confirm/', views.PaymentConfirmView.as_view(), name='confirm'),

    # --- TAMBAHAN UNTUK FITUR KATEGORI ---
    # Agar dropdown 'Category' di form pembayaran bisa diisi
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
]