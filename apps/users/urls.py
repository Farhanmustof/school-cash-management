from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Auth & Profile
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('toggle-dark-mode/', views.ToggleDarkModeView.as_view(), name='toggle-dark-mode'),
    
    # URL Manajemen User (Perbaikan tipe data ke UUID)
    path('management/', views.UserListView.as_view(), name='user_list'),
    path('management/add/', views.UserCreateView.as_view(), name='user_add'),
    path('', views.UserListView.as_view(), name='user_list_root'),
    
    # PERBAIKAN DI SINI: Menggunakan <uuid:pk> bukan <int:pk>
    path('management/edit/<uuid:pk>/', views.UserUpdateView.as_view(), name='user_edit'),
    path('management/delete/<uuid:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
]