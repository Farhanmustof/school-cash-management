
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from apps.notifications.models import Notification


@receiver(post_save, sender=Payment)
def notify_payment_status(sender, instance, created, **kwargs):
    if not created and instance.status == Payment.Status.CONFIRMED:
        if instance.student.user:
            Notification.objects.create(
                recipient=instance.student.user,
                title='Pembayaran Dikonfirmasi',
                message=f'Pembayaran {instance.invoice_number} sebesar Rp {instance.amount:,.0f} telah dikonfirmasi.',
                type=Notification.Type.PAYMENT,
                link=f'/payments/{instance.pk}/',
            )