"""API views using DRF."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.students.models import Student
from apps.payments.models import Payment
from django.db.models import Sum
from django.utils import timezone


class StudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.select_related('classroom').values(
            'id', 'nis', 'full_name', 'gender', 'is_active'
        )
        return Response({'results': list(students), 'count': len(students)})


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.select_related('student', 'category').values(
            'id', 'invoice_number', 'student__full_name',
            'category__name', 'amount', 'status', 'created_at'
        )[:50]
        return Response({'results': list(payments)})


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        return Response({
            'total_students': Student.objects.filter(is_active=True).count(),
            'monthly_income': float(Payment.objects.filter(
                status=Payment.Status.CONFIRMED,
                created_at__month=now.month, created_at__year=now.year,
            ).aggregate(total=Sum('amount'))['total'] or 0),
            'pending_payments': Payment.objects.filter(status=Payment.Status.PENDING).count(),
        })