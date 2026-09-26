import json
import datetime

# Di sinilah Anda memprogram logika untuk mengambil data dari web internet
# (Web Scraping / Panggil API luar)
# ...

# Contoh hasil setelah mengambil data dari internet:
data_baru = [
    {"id": 1, "nama": "Beras Premium", "harga": 16500, "sumber": "Web Disperindag", "trend": "stable"},
    {"id": 2, "nama": "Gula Pasir", "harga": 18000, "sumber": "Web Pasar Amuntai", "trend": "up"}
]

# Simpan hasil ke file JSON di dalam folder GitHub
with open('data_harga.json', 'w') as f:
    json.dump(data_baru, f)

print(f"Data berhasil diperbarui pada {datetime.datetime.now()}")
