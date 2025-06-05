from client import RestClient
from datetime import datetime
import data_processing
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
Login_email = os.getenv("LOGIN_EMAIL")
Login_password = os.getenv("LOGIN_PASSWORD")

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

# Dictionary of Keywords group for each brand
sub_brand_mapping = {
    "yoga1"  : ["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY"], 
    "yoga2"  :["LENOVO YOGA", "APPLE MACBOOK", "DELL INSPIRON 7000", "ACER SWIFT", "HP SPECTRE"],
    "yoga3"  :["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "NEC LAVIE", "HP ENVY"],  #Only for Japan
    "ideapad": ["LENOVO IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"] ,
    "loq"   : ["LENOVO LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "legion": ["LENOVO LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "tablet1": ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB", "XIAOMI PAD", "HUAWEI MATEPAD"], 
    "tablet2": ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB","REALME PAD", "APPLE IPAD"],
    "brand" : ["LENOVO"]
}

# Range tanggal
date_from = "2022-01-01"
date_to = "2025-05-31"

# Dictionary untuk simpan data per negara
all_data = {}

# Loop untuk setiap negara
def extract_google_trends_data(keywords_group):
    for code, country in countries.items():
        post_data = {
            0: {
                "location_name": country,
                "date_from": date_from,
                "date_to": date_to,
                "type": "web",
                "keywords": keywords_group
                ## "category_name": "Computers & Electronics"
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
                    for i, kw in enumerate(keywords_group):
                        row[f"{kw}: ({country})"] = values[i]
                    rows.append(row)

                df = pd.DataFrame(rows)
                all_data[country] = df
                print(f"✅ Data sukses diambil untuk {country}")
            except Exception as e:
                print(f"⚠️ Gagal memproses data untuk {country}: {e}")
        else:
            print(f"❌ Error untuk {country}: {response['status_message']}")
    return all_data

def select_subbrand(subbrand):
    ## This function processes data for a specific sub-brand
    # Check which subbrand is being extracted

    if subbrand not in sub_brand_mapping:
        raise ValueError(f"Sub-brand '{subbrand}' is not available. Please choice from thise list: {list(sub_brand_mapping.keys())}.")
    else:
        subbrand_keywords = sub_brand_mapping[subbrand]
        extracted_data = extract_google_trends_data(subbrand_keywords)
    return extracted_data

# Simpan semua sheet ke satu file Excel
print("=== Memulai Mengekstrak Data Google Trends ===")
brand_name = input("\nSelect which Lenovo sub brand you want to extract (example: 'legion', 'ideapad', etc): ").lower()
Google_trend_name = input("Masukkan nama file Google Trends (misal: 'hasil_google_trends.xlsx'): ")
if not Google_trend_name.endswith('.xlsx'):
        Google_trend_name = Google_trend_name + '.xlsx'


all_data = select_subbrand(brand_name)
output_path = "D:/Python/Lenovo Google Trend/Raw_file/"  + Google_trend_name
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