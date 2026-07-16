from django.contrib import admin
from .models import Payment, PaymentCategory, PaymentBill, Expenditure

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Menampilkan kolom penting di daftar pembayaran
    # Gunakan __iexact di filter status jika perlu, tapi di admin cukup seperti ini
    list_display = ['invoice_number', 'student', 'amount', 'status', 'payment_date', 'created_at']
    list_filter = ['status', 'method', 'payment_date']
    search_fields = ['invoice_number', 'student__full_name']
    
    # Tombol konfirmasi massal
    actions = ['make_confirmed']

    @admin.action(description='Konfirmasi pembayaran yang dipilih')
    def make_confirmed(self, request, queryset):
        queryset.update(status='confirmed') 
        self.message_user(request, "Pembayaran berhasil dikonfirmasi, saldo kas akan terupdate.")

@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    # PERBAIKAN: Hapus 'category' karena menyebabkan error E108 dan E116
    list_display = ['description', 'amount', 'date'] 
    list_filter = ['date']
    search_fields = ['description']

# Daftarkan model pendukung lainnya
admin.site.register(PaymentCategory)
admin.site.register(PaymentBill)