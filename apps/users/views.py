from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import ActivityLog

# Mengambil model User yang sedang aktif
User = get_user_model()

# --- AUTHENTICATION VIEWS ---

class LoginView(View):
    template_name = 'users/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return render(request, self.template_name)

    def post(self, request):
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            ActivityLog.objects.create(
                user=user,
                action="LOGIN",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return redirect('/dashboard/')
        else:
            messages.error(request, 'Username atau password salah.')
            return render(request, self.template_name)

class LogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            try:
                ActivityLog.objects.create(
                    user=request.user,
                    action="LOGOUT",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            except:
                pass
            logout(request)
        messages.success(request, 'Anda telah berhasil keluar.')
        return redirect('/auth/login/')

class ProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'users/profile.html')

class ToggleDarkModeView(View):
    def post(self, request):
        dark_mode = request.session.get('dark_mode', False)
        request.session['dark_mode'] = not dark_mode
        return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))


# --- MANAJEMEN USER VIEWS ---

@method_decorator(login_required, name='dispatch')
class UserListView(View):
    def get(self, request):
        # Hanya Super Admin atau Admin yang bisa akses
        if request.user.role not in ['super_admin', 'admin']:
            messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
            return redirect('/dashboard/')
            
        users = User.objects.all().order_by('-date_joined')
        return render(request, 'users/user_list.html', {'users': users})

# View untuk Tambah User Baru
class UserCreateView(SuccessMessageMixin, CreateView):
    model = User
    template_name = 'users/user_form.html'
    # Field yang bisa diisi di form
    fields = ['username', 'email', 'password', 'role', 'is_active']
    success_url = reverse_lazy('users:user_list')
    success_message = "User %(username)s berhasil dibuat!"

    def form_valid(self, form):
        # Enkripsi password sebelum disimpan ke database
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

# View untuk Edit Data User
class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'users/user_form.html'
    fields = ['username', 'email', 'role', 'is_active']
    success_url = reverse_lazy('users:user_list')
    success_message = "Data user berhasil diperbarui!"

# View untuk Konfirmasi Hapus User
class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:user_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "User berhasil dihapus.")
        return super().delete(request, *args, **kwargs)