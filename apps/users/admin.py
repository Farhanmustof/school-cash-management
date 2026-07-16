from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ActivityLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Menggunakan field yang pasti ada di database kamu (tanpa created_at)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    list_filter = ('is_staff', 'is_superuser', 'role')
    ordering = ('username',)
    
    # Tambahkan field khusus 'role' ke dalam form edit admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informasi Tambahan', {'fields': ('role',)}),
    )

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    # Menampilkan log aktivitas user
    list_display = ('user', 'action', 'ip_address', 'created_at') 
    list_filter = ('action', 'created_at') 
    search_fields = ('user__username', 'action')