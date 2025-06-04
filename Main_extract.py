from client import RestClient
from datetime import datetime
import data_processing
import pandas as pd

# Credential for API
Login_email = "gani@team.superfk.co"
Login_password = "f881f3d369097a8a"

# Initialize client
client = RestClient(Login_email, Login_password)

# Countries list
countries = {
    'ID': "Indonesia",
    'MY': "Malaysia"
}

# Keyword used, this is for testing purpose
keywords_group1 = [
    "LENOVO LEGION",
    "ASUS ROG",
    "HP OMEN",
    "ACER PREDATOR",
    "MSI GAMING"
]

# Dictionary of Keywords group for each brand
sub_brand_mapping = {
    "yoga"  : [
        ["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY"], 
        ["LENOVO YOGA", "APPLE MACBOOK", "DELL INSPIRON", "ACER SWIFT", "HP SPECTRE"]
    ],
    "ideapad": ["LENOVO IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"] ,
    "loq"   : ["LENOVO LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "legion": ["LENOVO LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "tablet": [
        ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB", "XIAOMI PAD", "HUAWEI MATEPAD"], 
        ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB","REALME PAD", "APPLE IPAD"]
    ],
    "brand" : "LENOVO"
}

# Set default date range
date_from = "2022-01-01"
date_to = "2025-05-31"

def extract_google_trends_data(keywords_group=keywords_group1):
    # Set empty dictionary to store all data
    all_data = {}

    # Fetching data using Custom Google Trends API
    for code, country in countries.items():
        post_data = {
            0: {
                "location_name": country,
                "date_from": date_from,
                "date_to": date_to,
                "type": "web",
                "keywords": keywords_group,
                "category_name": "Computers & Electronics"
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
                print(f"✅ Data extracted successfully for {country}")
            except Exception as e:
                print(f"⚠️ Fail to extract data for {country}: {e}")
        else:
            print(f"❌ Error for {country}: {response['status_message']}")
    return all_data

def select_subbrand(subbrand):
    ## This function processes data for a specific sub-brand

    # Check which subbrand is being extracted
    if subbrand not in sub_brand_mapping:
        raise ValueError(f"Sub-brand '{subbrand}' is not available. Please choice from thise list: {list(sub_brand_mapping.keys())}.")
    
    if subbrand not in ["yoga", "tablet"]:
        subbrand_keywords = sub_brand_mapping[subbrand]
        extracted_data = extract_google_trends_data(subbrand_keywords)
    else:
        subbrand_keywords_1 = sub_brand_mapping[subbrand][0]
        data_1 = extract_google_trends_data(subbrand_keywords_1)

        subbrand_keywords_2 = sub_brand_mapping[subbrand][1]
        data_2 = extract_google_trends_data(subbrand_keywords_2)

        # Removing duplicates and merging data
        extracted_data = {**data_1, **data_2}
        for country, df in extracted_data.items():
            df["country_name"] = country

        # Join and remove duplicates
        combined_df = pd.concat(extracted_data.values(), ignore_index=True)
        cleaned_df = combined_df.drop_duplicates(keep='first')

        # Return it back as a dictionary with country names as keys
        result_dict = {
            country: df.reset_index(drop=True)
            for country, df in cleaned_df.groupby("country_name")
        }
    return extracted_data

# Begin extraction
print("=== Google Trends Data Extractor ===")
brand_name = input("\nSelect which Lenovo sub brand you want to extract (example: 'legion', 'ideapad', etc): ").lower()
google_trend_name = input("Select file name you want to save as (example: 'google_trends_result.xlsx'): ")
if not google_trend_name.endswith('.xlsx'):
        google_trend_name = google_trend_name + '.xlsx'

print("\n=== Start Extracting Google Trends Data ===")
all_data = select_subbrand(brand_name)  # Change "legion" to the desired sub-brand
output_path = "D:/Python/Lenovo Google Trend/Raw file/"  + google_trend_name
with pd.ExcelWriter(output_path) as writer:
    for country, df in all_data.items():
        # Nama sheet maksimal 31 karakter, amanin
        sheet_name = country[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"📁 All data has been extracted and saved in {output_path}")

"""print("\n=== Start Processing Data===")
hasil = data_processing.process_trends_data(output_path, google_trend_name)

print("\nProcessing is complete! Here is preview of:\n")
print(hasil.head(10))"""