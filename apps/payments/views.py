"""Payment views."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Sum, Q
from .models import Payment, PaymentCategory, PaymentBill, Expenditure
from apps.students.models import Student
from .forms import PaymentForm, ExpenditureForm

# Real-time Update Features
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False

# --- VIEW UNTUK DASHBOARD (INDEX) ---
@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = 'index.html'

    def get(self, request):
        # Ambil 5 transaksi terbaru untuk tabel di index
        recent_payments = Payment.objects.select_related('student', 'category').all().order_by('-created_at')[:5]
        
        # Hitung saldo otomatis
        total_income = Payment.objects.filter(status='CONFIRMED').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Expenditure.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_balance = total_income - total_expense
        
        context = {
            'recent_payments': recent_payments,
            'total_balance': total_balance, # Kirim angka mentah, biarkan humanize di HTML yang memformat
            'monthly_income': total_income,
            'monthly_expense': total_expense,
        }
        return render(request, self.template_name, context)

# --- VIEW UNTUK DAFTAR TRANSAKSI (PAYMENTS LIST) ---
@method_decorator(login_required, name='dispatch')
class PaymentListView(View):
    template_name = 'payments/list.html'

    def get(self, request):
        # Query dasar dengan select_related untuk efisiensi
        payments = Payment.objects.select_related('student', 'category', 'confirmed_by').all()
        
        # Filter berdasarkan role siswa
        if request.user.role == 'siswa':
            payments = payments.filter(student__user=request.user)
        
        # Filter Status
        status_filter = request.GET.get('status')
        if status_filter:
            payments = payments.filter(status=status_filter)
            
        # Filter Waktu
        month = request.GET.get('month')
        year = request.GET.get('year', timezone.now().year)
        if month:
            payments = payments.filter(created_at__month=month, created_at__year=year)
        
        # Fitur Pencarian
        search = request.GET.get('q')
        if search:
            payments = payments.filter(
                Q(student__full_name__icontains=search) | 
                Q(invoice_number__icontains=search)
            )
            
        # --- PERBAIKAN: Hitung Total untuk bagian bawah tabel ---
        total_sum = payments.aggregate(Sum('amount'))['amount__sum'] or 0
            
        context = {
            'payments': payments.order_by('-created_at'),
            'total': total_sum, # Ini yang akan muncul di {{ total }} pada HTML
            'status_choices': Payment.Status.choices if hasattr(Payment, 'Status') else [('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('REJECTED', 'Rejected')],
            'active_filters': {
                'status': status_filter,
                'q': search
            }
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class PaymentCreateView(View):
    template_name = 'payments/form.html'

    def get(self, request):
        form = PaymentForm()
        categories = PaymentCategory.objects.all()
        return render(request, self.template_name, {
            'form': form, 
            'categories': categories, 
            'title': 'Input Pembayaran Baru'
        })

    def post(self, request):
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.created_by = request.user
            
            if request.user.role in ['super_admin', 'admin', 'bendahara']:
                payment.status = 'CONFIRMED'
                payment.confirmed_by = request.user
                payment.confirmed_at = timezone.now()
            else:
                payment.status = 'PENDING'
            
            payment.save()

            if CHANNELS_AVAILABLE:
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)('payments', {
                        'type': 'payment_update',
                        'data': {
                            'type': 'new_payment',
                            'invoice': payment.invoice_number,
                            'student': payment.student.full_name,
                            'amount': str(payment.amount),
                        }
                    })
                except:
                    pass

            messages.success(request, f'Pembayaran {payment.invoice_number} berhasil diproses.')
            return redirect('payments:list')
            
        return render(request, self.template_name, {'form': form, 'title': 'Tambah Pembayaran'})


@method_decorator(login_required, name='dispatch')
class PaymentConfirmView(View):
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        
        if request.user.role not in ['super_admin', 'admin', 'bendahara']:
            messages.error(request, 'Anda tidak memiliki otoritas untuk konfirmasi.')
            return redirect('payments:list')
            
        action = request.POST.get('action', 'approve')
        
        if action == 'approve':
            payment.status = 'CONFIRMED'
            payment.confirmed_by = request.user
            payment.confirmed_at = timezone.now()
            
            if hasattr(payment, 'bill') and payment.bill:
                payment.bill.is_paid = True
                payment.bill.save()
                
            messages.success(request, f'Pembayaran {payment.invoice_number} telah dikonfirmasi.')
        
        elif action == 'reject':
            payment.status = 'REJECTED'
            messages.warning(request, f'Pembayaran {payment.invoice_number} ditolak.')
            
        payment.save()
        return redirect('payments:list')


@method_decorator(login_required, name='dispatch')
class PaymentDetailView(View):
    def get(self, request, pk):
        if request.user.role == 'siswa':
            payment = get_object_or_404(Payment, pk=pk, student__user=request.user)
        else:
            payment = get_object_or_404(Payment, pk=pk)
            
        return render(request, 'payments/detail.html', {'payment': payment})


# --- MANAJEMEN KATEGORI ---

@method_decorator(login_required, name='dispatch')
class CategoryListView(View):
    template_name = 'payments/category_list.html'

    def get(self, request):
        if request.user.role not in ['super_admin', 'admin', 'bendahara']:
            messages.error(request, 'Akses ditolak.')
            return redirect('payments:list')
            
        categories = PaymentCategory.objects.all().order_by('name')
        return render(request, self.template_name, {'categories': categories})

@method_decorator(login_required, name='dispatch')
class CategoryCreateView(View):
    template_name = 'payments/category_form.html'

    def get(self, request):
        if request.user.role not in ['super_admin', 'admin', 'bendahara']:
            return redirect('payments:list')
        return render(request, self.template_name, {'title': 'Tambah Kategori'})

    def post(self, request):
        if request.user.role not in ['super_admin', 'admin', 'bendahara']:
            return redirect('payments:list')
        
        name = request.POST.get('name')
        cat_type = request.POST.get('type', 'in') 
        description = request.POST.get('description', '')

        if name:
            try:
                PaymentCategory.objects.create(
                    name=name, 
                    category_type=cat_type,
                    description=description
                )
            except:
                PaymentCategory.objects.create(
                    name=name, 
                    type=cat_type, 
                    description=description
                )
            messages.success(request, f'Kategori "{name}" berhasil ditambahkan.')
            return redirect('payments:category_list')
        
        messages.error(request, 'Nama kategori tidak boleh kosong.')
        return render(request, self.template_name, {'title': 'Tambah Kategori'})