"""URL Configuration for KasSekolah."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('students/', include('apps.students.urls')),
    path('classes/', include('apps.classes.urls')),
    path('payments/', include('apps.payments.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('laporan', include('apps.reports.urls')),
    path('users/', include('apps.users.urls')),
    path('admin-panel/users/', include('apps.users.urls')),
    # API
    path('api/', include('apps.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Root redirect
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)