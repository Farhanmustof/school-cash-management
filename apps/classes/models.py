from django.db import models
from django.conf import settings
import uuid

class AcademicYear(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)  # e.g. "2024/2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'academic_years'
        ordering = ['-start_date']
        # app_label memastikan Django tahu model ini milik aplikasi 'classes'
        app_label = 'classes' 

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            # Gunakan rujukan string untuk menghindari masalah saat inisialisasi
            AcademicYear.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    logo = models.ImageField(upload_to='schools/', blank=True, null=True)
    npsn = models.CharField(max_length=20, blank=True)
    principal = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'schools'
        app_label = 'classes'

    def __str__(self):
        return self.name


class Classroom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Menggunakan string reference 'School' karena berada di file yang sama
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='classrooms')
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, related_name='classrooms')
    
    name = models.CharField(max_length=50)  # e.g. "X IPA 1"
    grade = models.CharField(max_length=10) # X, XI, XII
    
    # Menggunakan settings.AUTH_USER_MODEL untuk rujukan User kustom
    homeroom_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='homeroom_classes', 
        limit_choices_to={'role': 'guru'}
    )
    class_treasurer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='treasurer_classes', 
        limit_choices_to={'role': 'siswa'}
    )
    
    monthly_dues = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classrooms'
        unique_together = ['school', 'academic_year', 'name']
        ordering = ['grade', 'name']
        app_label = 'classes'

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    @property
    def total_students(self):
        # Menggunakan related_name dari model Student (pastikan Student sudah benar)
        return self.students.filter(is_active=True).count()

    @property
    def total_collected(self):
        # Import lokal di dalam method untuk memutus circular dependency
        from apps.payments.models import Payment
        return Payment.objects.filter(
            student__classroom=self, 
            status=Payment.Status.CONFIRMED
        ).aggregate(total=models.Sum('amount'))['total'] or 0