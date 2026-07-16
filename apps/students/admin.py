from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    # Sesuaikan list_display dengan field yang ada di model kamu
    list_display = ['nis', 'full_name', 'classroom', 'gender', 'is_active', 'created_at']
    list_filter = ['classroom', 'gender', 'is_active']
    search_fields = ['nis', 'nisn', 'full_name']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']