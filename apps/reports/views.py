"""Reports views."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse
from django.db.models import Sum, Q
from apps.payments.models import Payment, Expenditure
from apps.students.models import Student
from apps.classes.models import Classroom # Import model Classroom
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm
from django.utils import timezone
import calendar

@method_decorator(login_required, name='dispatch')
class ReportDashboardView(View):
    def get(self, request):
        # Gunakan filter status sukses jika ada field status di model Payment Anda
        payments_qs = Payment.objects.all()
        
        total_pemasukan = payments_qs.aggregate(total=Sum('amount'))['total'] or 0
        total_pengeluaran = Expenditure.objects.aggregate(total=Sum('amount'))['total'] or 0
        saldo_akhir = total_pemasukan - total_pengeluaran
        total_siswa = Student.objects.count()
        
        # Tambahkan select_related ke classroom agar nama kelas muncul di dashboard
        transaksi_terakhir = payments_qs.select_related('student__classroom').order_by('-created_at')[:5]

        context = {
            'total_pemasukan': total_pemasukan,
            'total_pengeluaran': total_pengeluaran,
            'saldo_akhir': saldo_akhir,
            'total_siswa': total_siswa,
            'transaksi_terakhir': transaksi_terakhir,
        }
        return render(request, 'reports/dashboard.html', context)

@method_decorator(login_required, name='dispatch')
class PaymentReportView(View):
    def get(self, request):
        try:
            month = int(request.GET.get('month', timezone.now().month))
            year = int(request.GET.get('year', timezone.now().year))
        except (ValueError, TypeError):
            month = timezone.now().month
            year = timezone.now().year
        
        classroom_id = request.GET.get('classroom') # Tangkap filter kelas

        # Logika Range Tanggal
        last_day = calendar.monthrange(year, month)[1]
        start_date = timezone.datetime(year, month, 1)
        end_date = timezone.datetime(year, month, last_day, 23, 59, 59)

        # Filter dasar
        payments = Payment.objects.filter(
            created_at__range=(start_date, end_date)
        ).select_related('student__classroom').order_by('created_at')

        # Terapkan filter kelas jika dipilih
        if classroom_id:
            payments = payments.filter(student__classroom_id=classroom_id)

        # Hitung total dari data yang sudah difilter
        total = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        return render(request, 'reports/payments.html', {
            'payments': payments, 
            'total': total,
            'month': month, 
            'year': year,
            'classrooms': Classroom.objects.all(), # Kirim daftar kelas untuk dropdown filter
            'current_classroom': classroom_id,
        })

@method_decorator(login_required, name='dispatch')
class ExportPaymentPDFView(View):
    def get(self, request):
        try:
            month = int(request.GET.get('month', timezone.now().month))
            year = int(request.GET.get('year', timezone.now().year))
        except (ValueError, TypeError):
            month = timezone.now().month
            year = timezone.now().year
        
        classroom_id = request.GET.get('classroom') # Tangkap filter kelas untuk PDF

        last_day = calendar.monthrange(year, month)[1]
        start_date = timezone.datetime(year, month, 1)
        end_date = timezone.datetime(year, month, last_day, 23, 59, 59)
        
        # Ambil data dengan filter yang sama dengan tampilan web
        payments = Payment.objects.filter(
            created_at__range=(start_date, end_date)
        ).select_related('student__classroom').order_by('created_at')

        if classroom_id:
            payments = payments.filter(student__classroom_id=classroom_id)

        # --- Proses Pembuatan PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4), 
            rightMargin=30, 
            leftMargin=30, 
            topMargin=30, 
            bottomMargin=18
        )
        elements = []
        styles = getSampleStyleSheet()

        # Identifikasi nama kelas untuk judul laporan
        kelas_info = "Semua Kelas"
        if classroom_id:
            kelas_obj = Classroom.objects.filter(id=classroom_id).first()
            if kelas_obj:
                kelas_info = f"Kelas {kelas_obj.name}"

        # Judul Laporan
        title = f'LAPORAN PEMBAYARAN KAS - {kelas_info}'
        subtitle = f'PERIODE: {calendar.month_name[month].upper()} {year}'
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))

        # Header Tabel (Tambahkan kolom Kelas)
        data = [['No', 'Invoice', 'Nama Siswa', 'Kelas', 'Jumlah', 'Tanggal']]
        
        # Isi Tabel
        for i, p in enumerate(payments, 1):
            formatted_amount = "Rp {:,.0f}".format(p.amount).replace(",", ".")
            student_name = p.student.full_name if hasattr(p.student, 'full_name') else str(p.student)
            class_name = p.student.classroom.name if p.student.classroom else "-"
            
            data.append([
                str(i), 
                p.invoice_number, 
                student_name,
                class_name, # Kolom baru
                formatted_amount,
                p.created_at.strftime('%d/%m/%Y'),
            ])

        # Tambahkan baris TOTAL
        total_amount = sum(p.amount for p in payments)
        formatted_total = "Rp {:,.0f}".format(total_amount).replace(",", ".")
        data.append(['', '', '', 'TOTAL', formatted_total, ''])

        # Style Tabel (Sesuaikan colWidths karena ada tambahan kolom)
        table = Table(data, colWidths=[1*cm, 4*cm, 7*cm, 3*cm, 4*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Nama Siswa rata kiri
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (3, -1), (4, -1), 'Helvetica-Bold'), # Total Bold
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F3F4F6')]),
        ]))
        
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        filename = f"Laporan_Kas_{kelas_info.replace(' ', '_')}_{month}_{year}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response