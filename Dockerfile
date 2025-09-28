# Gunakan image dasar Python yang ringan
FROM python:3.10-slim

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching
COPY requirements.txt .

# Instal semua paket yang dibutuhkan
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode proyek Anda ke dalam kontainer
COPY . .

# BERITAHU BACK4APP BAHWA KONTAINER MENDENGARKAN DI PORT 8080
EXPOSE 8080
# Perintah untuk menjalankan aplikasi Anda saat kontainer dimulai
# Gunicorn akan berjalan di port 8080
# PERBAIKAN: Gunakan path absolut untuk memanggil gunicorn
CMD ["/usr/local/bin/gunicorn", "run:app", "--bind", "0.0.0.0:8080"]