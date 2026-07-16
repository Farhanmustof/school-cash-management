import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# GANTI BARIS IMPORT ANDA MENJADI INI:
from django.contrib.auth import get_user_model
User = get_user_model()

# Lanjutkan kode Anda
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'password123')
    print("Superuser created!")