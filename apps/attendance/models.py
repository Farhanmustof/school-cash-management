
"""Attendance models."""
from django.db import models
from apps.students.models import Student
from apps.users.models import User
import uuid


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'hadir', 'Hadir'
        ABSENT = 'absen', 'Absen'
        SICK = 'sakit', 'Sakit'
        PERMISSION = 'izin', 'Izin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    check_in_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendances'
        unique_together = ['student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"