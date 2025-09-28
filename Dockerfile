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

# Perintah untuk menjalankan aplikasi Anda saat kontainer dimulai
# Gunicorn akan berjalan di port 8080
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8080"]