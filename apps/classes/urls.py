
from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.ClassroomListView.as_view(), name='list'),
    path('create/', views.ClassroomCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ClassroomDetailView.as_view(), name='detail'),
]