from client import RestClient
from datetime import datetime
import data_processing
import pandas as pd

Login_email = "gani@team.superfk.co"
Login_password = "f881f3d369097a8a"

# Initialize client
client = RestClient(Login_email, Login_password)

# Daftar negara yang akan di-loop
countries = {
    'ID': "Indonesia",
    'MY': "Malaysia",
    'SG': "Singapore",
    'PH': "Philippines",
    'VN': "Vietnam",
    'TH': "Thailand",
    'TW': "Taiwan",
    'HK': "Hong Kong",
    'KR': "South Korea",
    'JP': "Japan",
    'IN': "India",
    'AU': "Australia",
    'NZ': "New Zealand"
}

# Keyword yang digunakan
keywords = [
    "LENOVO LEGION",
    "ASUS ROG",
    "HP OMEN",
    "ACER PREDATOR",
    "MSI GAMING"
]

# Range tanggal
date_from = "2025-03-01"
date_to = "2025-03-31"

# Dictionary untuk simpan data per negara
all_data = {}

# Simpan semua sheet ke satu file Excel
print("=== Memulai Mengekstrak Data Google Trends ===")
Google_trend_name = input("Masukkan nama file Google Trends (misal: 'hasil_google_trends.xlsx'): ")
if not Google_trend_name.endswith('.xlsx'):
        Google_trend_name = Google_trend_name + '.xlsx'

# Loop untuk setiap negara
for code, country in countries.items():
    post_data = {
        0: {
            "location_name": country,
            "date_from": date_from,
            "date_to": date_to,
            "type": "web",
            "keywords": keywords
        }
    }

    response = client.post("/v3/keywords_data/google_trends/explore/live", post_data)

    if response["status_code"] == 20000:
        try:
            result = response["tasks"][0]["result"][0]
            trend_data = result["items"][0]["data"]

            rows = []
            for entry in trend_data:
                date_str = datetime.strptime(entry["date_from"], "%Y-%m-%d").strftime("%d/%m/%Y")
                values = [v if v is not None else 0 for v in entry["values"]]
                row = {"Day": date_str}
                for i, kw in enumerate(keywords):
                    row[f"{kw}: ({country})"] = values[i]
                rows.append(row)

            df = pd.DataFrame(rows)
            all_data[country] = df
            print(f"✅ Data sukses diambil untuk {country}")
        except Exception as e:
            print(f"⚠️ Gagal memproses data untuk {country}: {e}")
    else:
        print(f"❌ Error untuk {country}: {response['status_message']}")

output_path = "D:/Python/Lenovo Google Trend/Raw file/"  + Google_trend_name
with pd.ExcelWriter(output_path) as writer:
    for country, df in all_data.items():
        # Nama sheet maksimal 31 karakter, amanin
        sheet_name = country[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"📁 Semua data selesai disimpan di {output_path}")
print("\n=== Memulai memproses data===")
hasil = data_processing.process_trends_data(output_path, Google_trend_name)

print("\nProses selesai! Berikut adalah preview hasil akhir:\n")
print(hasil.head(10))