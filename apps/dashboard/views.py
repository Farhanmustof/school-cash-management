"""Dashboard views."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.admin.models import LogEntry

from apps.payments.models import Payment, Expenditure
from apps.students.models import Student
from apps.classes.models import Classroom, AcademicYear
from apps.notifications.models import Announcement
# Pastikan import model Iuran/Fee jika ada untuk 'Iuran Aktif'
# from apps.payments.models import Fee 

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        user = request.user
        if not hasattr(user, 'role') or not user.role:
            return render(request, 'dashboard/default.html', {
                'message': 'Role pengguna tidak ditemukan dalam sistem.'
            })

        context = self.get_context_by_role(user)
        return render(request, f'dashboard/{user.role}.html', context)

    def get_context_by_role(self, user):
        now = timezone.now()
        current_year = AcademicYear.objects.filter(is_active=True).first()

        # 1. Definisi filter status sukses (Global)
        # Gunakan nama variabel ini secara konsisten di .filter()
        success_filter = Q(status__iexact='confirmed') | \
                 Q(status__iexact='success') | \
                 Q(status__iexact='terkonfirmasi') | \
                 Q(status__iexact='lunas') | \
                 Q(status__iexact='dikonfirmasi')

        base_context = {
            'current_year': current_year,
            'today': now,
            'announcements': Announcement.objects.filter(is_active=True).order_by('-created_at')[:5],
        }

        if user.role in ['super_admin', 'admin', 'bendahara']:
            # --- Perbaikan Logika Keuangan ---
            
            # Filter pemasukan berdasarkan status sukses
            payments_qs = Payment.objects.filter(success_filter)
            
            # Jika ada filter tahun ajaran aktif, saring pemasukan tahun ini saja
            if current_year:
                payments_qs = payments_qs.filter(created_at__year=now.year) # Atau filter berdasarkan relasi AcademicYear jika ada

            # Hitung Total Pemasukan
            total_income = payments_qs.aggregate(total=Sum('amount'))['total'] or 0

            # Hitung Total Pengeluaran
            total_expenditure = Expenditure.objects.aggregate(total=Sum('amount'))['total'] or 0

            # Total Saldo (Pemasukan - Pengeluaran)
            total_balance = total_income - total_expenditure

            # Transaksi Terakhir (Gunakan select_related untuk performa)
            recent_payments = Payment.objects.select_related('student').order_by('-created_at')[:10]

            # Statistik Per Kelas
            # Catatan: status_sukses di sini menggunakan path relasi dari Classroom -> Student -> Payment
            annotation_filter = Q(students__payments__status__iexact='confirmed') | \
                                Q(students__payments__status__iexact='terkonfirmasi') | \
                                Q(students__payments__status__iexact='success')
            
            class_stats = Classroom.objects.annotate(
                total_money=Sum('students__payments__amount', filter=annotation_filter)
            )

            base_context.update({
                'total_students': Student.objects.filter(is_active=True).count(),
                'total_classes': Classroom.objects.count(),
                'total_income': total_income,
                'total_expenditure': total_expenditure,
                'total_balance': total_balance,
                'pending_payments': Payment.objects.filter(Q(status__iexact='pending') | Q(status='-') | Q(status__iexact='waiting')).count(),
                'recent_payments': recent_payments,
                'class_stats': class_stats,
                'activity_logs': LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:5],
                # 'active_fee': Fee.objects.filter(is_active=True).first(), # Contoh jika ada model Iuran
            })

        elif user.role == 'guru':
            # 1. Ambil kelas yang diampu oleh guru ini
            my_classes = Classroom.objects.filter(homeroom_teacher=user)
            
            # 2. Hitung total uang kas per masing-masing kelas secara otomatis
            annotation_filter = Q(students__payments__status__iexact='confirmed') | \
                                Q(students__payments__status__iexact='terkonfirmasi') | \
                                Q(students__payments__status__iexact='success')
            
            my_classes_with_stats = my_classes.annotate(
                total_money=Sum('students__payments__amount', filter=annotation_filter)
            )

            # 3. Hitung total seluruh kas gabungan dari kelas-kelas guru ini
            total_kas_kelas = Payment.objects.filter(
                success_filter,
                student__classroom__in=my_classes
            ).aggregate(total=Sum('amount'))['total'] or 0

            base_context.update({
                'classrooms': my_classes_with_stats, # Menggunakan kelas yang sudah ada hitungan uangnya
                'total_kas_kelas': total_kas_kelas,
                'transaksi_kelas': Payment.objects.filter(student__classroom__in=my_classes).order_by('-created_at')[:5]
            })

        elif user.role == 'siswa':
            try:
                student = Student.objects.get(user=user)
                total_paid = Payment.objects.filter(student=student).filter(success_filter).aggregate(total=Sum('amount'))['total'] or 0
                
                base_context.update({
                    'student': student,
                    'my_payments': Payment.objects.filter(student=student).order_by('-created_at')[:5],
                    'total_paid': total_paid,
                })
            except Student.DoesNotExist:
                base_context.update({'error': 'Profil siswa belum dikonfigurasi.'})

        return base_context

@method_decorator(login_required, name='dispatch')
class DashboardStatsAPI(View):
    def get(self, request):
        now = timezone.now()
        success_filter = Q(status__iexact='confirmed') | Q(status__iexact='terkonfirmasi') | Q(status__iexact='success')

        total_income_month = Payment.objects.filter(
            success_filter,
            created_at__year=now.year,
            created_at__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        data = {
            'total_income': float(total_income_month),
            'pending_count': Payment.objects.filter(Q(status__iexact='pending') | Q(status='-')).count(),
            'today_count': Payment.objects.filter(created_at__date=now.date()).count(),
        }
        return JsonResponse(data)