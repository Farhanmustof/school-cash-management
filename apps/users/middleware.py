"""Custom middleware for users app."""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import ActivityLog


class ActivityLogMiddleware(MiddlewareMixin):
    """Log semua request pengguna."""
    EXCLUDED_PATHS = ['/static/', '/media/', '/favicon.ico']

    def process_request(self, request):
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return None
        
        # PERBAIKAN: Ganti ActivityLog.Action.VIEW menjadi string "POST"
        if request.user.is_authenticated and request.method == 'POST':
            ActivityLog.objects.create(
                user=request.user,
                action="POST", # Pakai string manual agar tidak perlu migrations
                ip_address=self.get_client_ip(request)
            )
        return None

    def get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR')


class RoleProtectionMiddleware(MiddlewareMixin):
    """Middleware proteksi role-based access."""
    ROLE_PATHS = {
        '/admin-panel/': ['super_admin', 'admin'],
        '/reports/': ['super_admin', 'admin', 'bendahara'],
    }

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        # Pastikan user memiliki atribut role sebelum dicek
        user_role = getattr(request.user, 'role', 'siswa')
        
        for path, allowed_roles in self.ROLE_PATHS.items():
            if request.path.startswith(path):
                if user_role not in allowed_roles:
                    messages.error(request, 'Anda tidak memiliki akses ke halaman ini.')
                    return redirect('/dashboard/')
        return None