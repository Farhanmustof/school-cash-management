"""Notification and Announcement models."""
from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    class Type(models.TextChoices):
        PAYMENT = 'payment', 'Pembayaran'
        REMINDER = 'reminder', 'Pengingat'
        ANNOUNCEMENT = 'announcement', 'Pengumuman'
        SYSTEM = 'system', 'Sistem'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        verbose_name="Penerima"
    )
    title = models.CharField(max_length=200, verbose_name="Judul")
    message = models.TextField(verbose_name="Pesan")
    type = models.CharField(
        max_length=20, 
        choices=Type.choices, 
        default=Type.SYSTEM,
        verbose_name="Jenis"
    )
    is_read = models.BooleanField(default=False, verbose_name="Sudah Dibaca")
    link = models.CharField(max_length=500, blank=True, verbose_name="Tautan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Waktu")

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = "Notifikasi"
        verbose_name_plural = "Data Notifikasi"

    def __str__(self):
        return f"{self.recipient} - {self.title}"


class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Judul Pengumuman")
    content = models.TextField(verbose_name="Isi Pengumuman")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Penulis"
    )
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        verbose_name = "Pengumuman"
        verbose_name_plural = "Data Pengumuman"

    def __str__(self):
        return self.title