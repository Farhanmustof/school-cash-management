from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('<uuid:pk>/read/', views.MarkReadView.as_view(), name='mark-read'),
    path('read-all/', views.MarkAllReadView.as_view(), name='read-all'),
    # Path baru untuk tombol "Buat/Daftar Pengumuman"
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement_list'),
]