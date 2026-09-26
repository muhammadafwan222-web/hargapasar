import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL target (Ganti dengan URL web sumber data harga komoditas)
TARGET_URL = "https://sihapok.hulusungaiselatankab.go.id/semua"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
}

def clean_text(text):
    """Membersihkan spasi berlebih dan baris baru dari teks HTML."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def extract_numeric_price(price_str):
    """
    Mengekstrak nilai angka bersih dari format string harga.
    Contoh: 'Rp 26.000 (▼ Rp 1.000)' -> 26000
    """
    if not price_str or "belum" in price_str.lower():
        return None
    
    # Ambil bagian sebelum tanda kurung (harga utama)
    main_price = price_str.split("(")[0]
    digits = re.sub(r"[^\d]", "", main_price)
    return int(digits) if digits else None

def parse_commodity_table(html_content):
    """Memproses HTML dan mengekstrak tabel harga komoditas."""
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    
    if not table:
        print("[-] Tabel tidak ditemukan pada HTML.")
        return []

    rows = table.find_all("tr")
    extracted_data = []
    current_category = "Umum"

    for row in rows:
        headers = row.find_all("th")
        cols = row.find_all("td")

        # Jika baris merupakan header kategori/sub-judul
        if headers and len(headers) == 1:
            current_category = clean_text(headers[0].text)
            continue

        if cols:
            row_cells = [clean_text(col.text) for col in cols]

            # Memastikan struktur kolom sesuai (Nama, Satuan, Kandangan, Negara, Banjarmasin, Tanjung, Persediaan)
            if len(row_cells) >= 7:
                item = {
                    "Kategori": current_category,
                    "Nama_Bahan": row_cells[0],
                    "Satuan": row_cells[1],
                    "Pasar_Kandangan": row_cells[2],
                    "Harga_Kandangan_Rp": extract_numeric_price(row_cells[2]),
                    "Pasar_Negara": row_cells[3],
                    "Harga_Negara_Rp": extract_numeric_price(row_cells[3]),
                    "IHK_Banjarmasin": row_cells[4],
                    "Harga_Banjarmasin_Rp": extract_numeric_price(row_cells[4]),
                    "IHK_Tanjung": row_cells[5],
                    "Harga_Tanjung_Rp": extract_numeric_price(row_cells[5]),
                    "Persediaan": row_cells[6]
                }
                extracted_data.append(item)

    return extracted_data

def main():
    # Set True jika ingin menguji dengan file HTML lokal (misal: 'data.html')
    USE_LOCAL_FILE = False
    LOCAL_FILE_PATH = "data.html"

    try:
        if USE_LOCAL_FILE:
            print(f"[+] Membaca file lokal: {LOCAL_FILE_PATH}")
            with open(LOCAL_FILE_PATH, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            print(f"[+] Mengunduh data dari: {TARGET_URL}")
            response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            html_content = response.text

        # Parsing data
        data = parse_commodity_table(html_content)

        if data:
            # Export ke CSV menggunakan Pandas
            df = pd.DataFrame(data)
            csv_path = "harga_komoditas.csv"
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(f"[✓] Data berhasil disimpan ke CSV: {csv_path}")

            # Export ke JSON
            json_path = "harga_komoditas.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[✓] Data berhasil disimpan ke JSON: {json_path}")

            # Tampilkan Ringkasan
            print("\n--- Pratinjau Hasil Scraping ---")
            print(df[["Nama_Bahan", "Satuan", "Pasar_Kandangan", "IHK_Banjarmasin"]].head())
        else:
            print("[-] Tidak ada data yang berhasil diekstrak.")

    except Exception as e:
        print(f"[!] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
