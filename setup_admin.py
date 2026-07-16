import os
import django

# Setup environment Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def setup_admin():
    User = get_user_model()
    username = 'admin'
    email = 'admin@sekolah.com'
    password = 'password123'
    
    # Mencari user atau membuatnya jika belum ada
    user, created = User.objects.get_or_create(username=username)
    
    if created:
        user.set_password(password)
        user.email = email
        print(f"Membuat user baru: {username}")
    else:
        print(f"User {username} sudah ada, melakukan update akses...")

    # Memastikan hak akses penuh (Superuser & Staff)
    user.is_staff = True
    user.is_superuser = True
    
    # Jika Anda memiliki field 'role', pastikan diupdate
    if hasattr(user, 'role'):
        user.role = 'admin'
        
    user.save()
    print(f"Superuser '{username}' telah disiapkan dengan hak akses penuh.")

if __name__ == '__main__':
    setup_admin()