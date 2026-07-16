from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import Notification, Announcement

@method_decorator(login_required, name='dispatch')
class NotificationListView(View):
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user)
        return render(request, 'notifications/list.html', {'notifications': notifications})

@method_decorator(login_required, name='dispatch')
class MarkReadView(View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'ok'})

@method_decorator(login_required, name='dispatch')
class MarkAllReadView(View):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})

# View Baru untuk Pengumuman agar tidak Page Not Found
@method_decorator(login_required, name='dispatch')
class AnnouncementListView(View):
    def get(self, request):
        announcements = Announcement.objects.filter(is_active=True)
        return render(request, 'notifications/announcement_list.html', {
            'announcements': announcements
        })