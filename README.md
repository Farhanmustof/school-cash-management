# Kas Sekolah

Sistem Manajemen Kas Sekolah berbasis Django.

## Deskripsi
Proyek ini adalah sistem untuk mengelola pencatatan kas sekolah, mencakup pembayaran, kehadiran siswa, dan laporan.

## Fitur
- Manajemen Siswa
- Manajemen Pembayaran
- Pencatatan Kehadiran
- Pelaporan Kas
- Sistem Notifikasi
- Dashboard untuk Admin, Bendahara, Guru, dan Siswa

## Prasyarat
- Python 3.x
- MySQL
- Redis (untuk Celery)

## Instalasi

1. Clone repositori ini:
   ```bash
   git clone <URL_REPOSITORI_ANDA>
   cd kas_sekolah
   ```

2. Buat dan aktifkan virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurasi Environment:
   - Salin file `config/.env.example` (jika ada) ke `config/.env` atau buat file baru `config/.env` dengan konten berikut:
     ```env
     SECRET_KEY=django-insecure-sekolah-pro-key-gabungan
     DB_NAME=db_kas_sekolah
     DB_USER=root
     DB_PASSWORD=your_password_here
     DB_HOST=127.0.0.1
     DB_PORT=3306
     ```
   - Sesuaikan nilai `DB_PASSWORD` dengan kata sandi database MySQL Anda.

5. Jalankan migrasi database:
   ```bash
   python manage.py migrate
   ```

6. Jalankan server pengembangan:
   ```bash
   python manage.py runserver
   ```
