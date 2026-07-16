import uuid
import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.students.models import Student

class PaymentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_monthly = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_categories'

    def __str__(self):
        return self.name

class PaymentBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bills')
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_bills'

    def __str__(self):
        return f"{self.student.full_name} - {self.category.name}"

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Menunggu Konfirmasi'
        CONFIRMED = 'confirmed', 'Terkonfirmasi'
        REJECTED = 'rejected', 'Ditolak'

    class Method(models.TextChoices):
        CASH = 'cash', 'Tunai'
        TRANSFER = 'transfer', 'Transfer Bank'
        MIDTRANS = 'midtrans', 'Midtrans'
        XENDIT = 'xendit', 'Xendit'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    bill = models.ForeignKey(PaymentBill, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    proof_image = models.ImageField(upload_to='payments/proofs/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='confirmed_payments'
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    month = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name='created_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.student.full_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_invoice_number():
        now = timezone.now()
        date_str = now.strftime("%Y/%m") # Hasil: 2026/05
        prefix = f"INV/{date_str}/"
        
        # Mengambil invoice terakhir yang memiliki prefix bulan/tahun yang sama
        last_payment = Payment.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()
        
        if last_payment:
            try:
                # Memecah string 'INV/2026/05/0001' untuk mengambil angka terakhir
                last_number = int(last_payment.invoice_number.split('/')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
            
        return f"{prefix}{new_number:04d}"

class Expenditure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to='expenditures/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expenditures'
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount}"