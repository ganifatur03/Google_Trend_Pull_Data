import pandas as pd
from datetime import datetime

## This file is used to process Google Trends data from an Excel file .

# Dictionary untuk nama hari
hari_dict = {
    0: "Senin",
    1: "Selasa",
    2: "Rabu",
    3: "Kamis",
    4: "Jumat",
    5: "Sabtu",
    6: "Minggu"
}

# Dictionary untuk negara
negara_dict = {
    'Indonesia': "INDONESIA",
    'Malaysia': "MALAYSIA",
    'Singapore': "SINGAPORE",
    'Philippines': "PHILIPPINES",
    'Vietnam': "VIETNAM",
    'Thailand': "THAILAND",
    'Taiwan': "TAIWAN",
    'Hong Kong': "HONG KONG",
    'South Korea': "SOUTH KOREA",
    'Japan': "JAPAN",
    'India': "INDIA",
    'Australia': "AUSTRALIA",
    'New Zealand': "NEW ZEALAND"
}

region_mapping = {
    "INDONESIA": "CAP",
    "MALAYSIA": "CAP",
    "SINGAPORE": "CAP",
    "PHILIPPINES": "CAP",
    "VIETNAM": "CAP",
    "THAILAND": "CAP",
    "TAIWAN": "CAP",
    "HONG KONG": "CAP",
    "SOUTH KOREA": "CAP",
    "JAPAN": "JP",
    "INDIA": "IN",
    "AUSTRALIA": "ANZ",
    "NEW ZEALAND": "ANZ"
}

sub_brand_mapping = {
    "Yoga": [["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY"], 
             ["LENOVO YOGA", "APPLE MACBOOK", "DELL INSPIRON", "ACER SWIFT", "HP SPECTRE"]],
    "Ideapad": ["LENOVO IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"] ,
    "LOQ": ["LENOVO LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "Legion": ["LENOVO LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "Tablet": [["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB", "XIAOMI PAD", "HUAWEI MATEPAD"], 
               ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB","REALME PAD", "APPLE IPAD"]],
    "Brand": "LENOVO"
}


def process_trends_data(excel_path, file_name=None):
    """Fungsi untuk memproses data trend dan menghasilkan ringkasan mingguan"""
    xls = pd.ExcelFile(excel_path)
    nama_sheet = xls.sheet_names
    
    data_tren_list = []
    
    for sheet in nama_sheet:
        df = pd.read_excel(xls, sheet)
        
        # Clean column names by removing ": (country name)"
        df.columns = df.columns.str.split(':').str[0]
        
        # Modified date parsing to handle different formats
        try:
            df['Day'] = pd.to_datetime(df['Day'], format='%d/%m/%Y')  # Try DD/MM/YYYY first
        except:
            try:
                df['Day'] = pd.to_datetime(df['Day'])  # Let pandas detect format
            except:
                print(f"Warning: Date parsing issue in sheet {sheet}. Please check the date format.")
                continue
        
        # Tambahkan kolom informasi negara, region, dan hari
        df['Day'] = df['Day'].dt.date  # Convert to date only

        nama_country = negara_dict.get(sheet, "Unknown")
        region = region_mapping.get(nama_country, "Unknown")  # Get region based on country name
        df['Country'] = nama_country
        df['Region'] = region
        
        # Konversi format DataFrame
        data_tren = df.melt(
            id_vars=['Day', 'Country', 'Region'],  # Added 'Region' to id_vars
            var_name='Search term',
            value_name='Trend index'
        )
        data_tren_list.append(data_tren)
    
    # Gabungkan semua data
    hasil_akhir = pd.concat(data_tren_list, ignore_index=True)
    hasil_akhir['Trend index'] = hasil_akhir['Trend index'].round(0)

    # Memisahkan data berdasarkan Region
    region_CAP = hasil_akhir[hasil_akhir['Region'] == 'CAP']
    region_JP = hasil_akhir[hasil_akhir['Region'] == 'JP']  
    region_IN = hasil_akhir[hasil_akhir['Region'] == 'IN']
    region_ANZ = hasil_akhir[hasil_akhir['Region'] == 'ANZ']
    
    # Simpan hasil ke file Excel baru
    if file_name:
        output_summary = excel_path.split('Raw', 1)[0] + "Processed file/" + file_name + " - Processed.xlsx"
    else:
        output_summary = excel_path.split('.', 1)[0] + " - Processed.xlsx"
    with pd.ExcelWriter(output_summary, engine='openpyxl') as writer:
        hasil_akhir.to_excel(writer, index=False)
        region_CAP.to_excel(writer, index=False, sheet_name='CAP9')
        region_JP.to_excel(writer, index=False, sheet_name='JP')
        region_IN.to_excel(writer, index=False, sheet_name='IN')
        region_ANZ.to_excel(writer, index=False, sheet_name='ANZ')
    print(f"\nRingkasan trend telah disimpan ke '{output_summary}'")
    
    return hasil_akhir

def main():
    print("=== Google Trends Data Processor ===")
    print("\n1. Langkah pertama: Membaca file CSV")
    google_trends_file = input("Masukkan path file Google Trends (misal: 'data/google_trends.xlsx'): ")

    print("\n2. Langkah kedua: Memproses data trend")
    hasil = process_trends_data(google_trends_file)
    
    print("\nProses selesai! Berikut adalah preview hasil akhir:\n")
    print(hasil.head(20))

if __name__ == "__main__":
    main() 