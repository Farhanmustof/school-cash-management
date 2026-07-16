"""Celery configuration for KasSekolah."""
import os
from celery import Celery

# UBAH INI: Arahkan langsung ke config.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('kassekolah')

# namespace='CELERY' artinya semua config celery di settings.py 
# harus diawali dengan kata CELERY_ (contoh: CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')