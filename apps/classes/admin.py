
from django.contrib import admin
from .models import Classroom, AcademicYear, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'npsn', 'phone', 'email']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'academic_year', 'homeroom_teacher', 'total_students', 'is_active']
    list_filter = ['grade', 'academic_year', 'is_active']