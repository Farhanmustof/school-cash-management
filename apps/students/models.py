from django.db import models
from django.conf import settings
import uuid
import qrcode
import io
from django.core.files.base import ContentFile

class Student(models.Model):
    # Definisi Pilihan Gender
    class Gender(models.TextChoices):
        MALE = 'L', 'Laki-laki'
        FEMALE = 'P', 'Perempuan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 1. Foreign Key dengan Verbose Name Bahasa Indonesia
    classroom = models.ForeignKey(
        'classes.Classroom', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students',
        verbose_name="Kelas"
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='student_profile', 
        null=True, 
        blank=True,
        verbose_name="Akun Pengguna"
    )
    
    # 2. Field Identitas
    nis = models.CharField(max_length=20, unique=True, verbose_name="NIS")
    nisn = models.CharField(max_length=20, blank=True, verbose_name="NISN")
    full_name = models.CharField(max_length=200, verbose_name="Nama Lengkap")
    gender = models.CharField(
        max_length=1, 
        choices=Gender.choices, 
        verbose_name="Jenis Kelamin"
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tanggal Lahir")
    birth_place = models.CharField(max_length=100, blank=True, verbose_name="Tempat Lahir")
    address = models.TextField(blank=True, verbose_name="Alamat")
    phone = models.CharField(max_length=20, blank=True, verbose_name="No. Telepon")
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, verbose_name="Foto")
    qr_code = models.ImageField(upload_to='students/qr/', blank=True, null=True, verbose_name="QR Code")
    
    # 3. Data Orang Tua
    parent_name = models.CharField(max_length=200, blank=True, verbose_name="Nama Orang Tua")
    parent_phone = models.CharField(max_length=20, blank=True, verbose_name="Telepon Orang Tua")
    parent_email = models.EmailField(blank=True, verbose_name="Email Orang Tua")
    
    parent_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='children', 
        limit_choices_to={'role': 'orang_tua'},
        verbose_name="Akun Orang Tua"
    )
    
    # 4. Status & Audit
    is_active = models.BooleanField(default=True, verbose_name="Status Aktif")
    notes = models.TextField(blank=True, verbose_name="Catatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui pada")

    class Meta:
        db_table = 'students'
        ordering = ['full_name']
        verbose_name = "Siswa"
        verbose_name_plural = "Data Siswa"

    def __str__(self):
        # PERBAIKAN: Mengembalikan full_name saja agar di Dashboard tampil rapi
        return self.full_name

    def generate_qr_code(self):
        """Generate QR code untuk siswa."""
        try:
            qr_data = f"STUDENT:{self.nis}:{self.full_name}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_{self.nis}.png'
            
            # Menggunakan save=False untuk mencegah rekursi (infinite loop)
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        except Exception as e:
            print(f"Error generating QR Code: {e}")

    def save(self, *args, **kwargs):
        # Generate QR Code hanya jika belum ada
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    @property
    def total_paid(self):
        from apps.payments.models import Payment
        # Mengambil total pembayaran yang sudah dikonfirmasi
        return self.payments.filter(
            status='CONFIRMED'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def total_unpaid(self):
        from apps.payments.models import PaymentBill
        # Mengambil total tagihan yang belum lunas
        total_bill = self.bills.filter(is_paid=False).aggregate(
            total=models.Sum('amount'))['total'] or 0
        return total_bill