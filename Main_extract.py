from dotenv import load_dotenv
from client import RestClient
from datetime import datetime
import pandas as pd
import os

load_dotenv()
Login_email = os.getenv("LOGIN_EMAIL")
Login_password = os.getenv("LOGIN_PASSWORD")

# Initialize client
client = RestClient(Login_email, Login_password)

# Countries list
countries = {
    'ID': "Indonesia",
    'WORLD': None       # ommit location countries to get worldwide data
}

region_mapping = {
    "Indonesia": "CAP",
    "Malaysia": "CAP",
    "Singapore": "CAP",
    "Philippines": "CAP",
    "Vietnam": "CAP",
    "Thailand": "CAP",
    "Taiwan": "CAP",
    "Hong Kong": "CAP",
    "South Korea": "CAP",
    "Japan": "JP",
    "India": "IN",
    "Australia": "ANZ",
    "New Zealand": "ANZ",
    "Worldwide": "WORLD"
}


# Dictionary of Keywords group for each brand
sub_brand_mapping = {
    "yoga": [["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY"], 
             ["LENOVO YOGA", "APPLE MACBOOK", "DELL INSPIRON", "ACER SWIFT", "HP SPECTRE"]],
    "ideapad": ["LENOVO IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"] ,
    "loq": ["LENOVO LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "legion": ["LENOVO LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "tablet": [["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB", "XIAOMI PAD", "HUAWEI MATEPAD"], 
               ["LENOVO TAB", "LENOVO TABLET", "SAMSUNG GALAXY TAB","REALME PAD", "APPLE IPAD"]],
    "brand": "LENOVO"
}

# Range tanggal
date_from = "2022-01-01"
date_to = "2025-05-31"

# List to store all trend data
data_trend_list = []

# Loop untuk setiap negara
def extract_google_trends_data(keywords_group, countries_subset=None):
    selected_countries = countries_subset if countries_subset is not None else countries

    for code, country in selected_countries.items():
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

                # Add Country and Region columns
                if country is None:
                    df['Country'] = "Worldwide"
                    df['Region'] = "WORLD"
                else:
                    region = region_mapping.get(country, "Unknown")
                    df['Country'] = country
                    df['Region'] = region


                # Clean column names by removing ": (country)"
                df.columns = df.columns.str.replace(r":\s*\(.+?\)", "", regex=True)

                # Parse Day column
                try:
                    df['Day'] = pd.to_datetime(df['Day'], format='%d/%m/%Y')
                except:
                    try:
                        df['Day'] = pd.to_datetime(df['Day'])
                    except:
                        print(f"Date parsing issue for {country}. Please check the date format.")
                        continue
                df['Day'] = df['Day'].dt.date  # Keep only the date part

                # Convert to long format
                data_trend = df.melt(
                    id_vars=['Day', 'Country', 'Region'],
                    var_name='Search term',
                    value_name='Trend index'
                )

                data_trend_list.append(data_trend)
                print(f"✅ Successfully extracted data for {country}")

            except Exception as e:
                print(f"⚠️ Failed to extract data for {country}: {e}")
        else:
            print(f"API error for {country}: {response['status_message']}")
    
    # Combine all trend data into a single DataFrame
    final_result = pd.concat(data_trend_list, ignore_index=True)
    return final_result

def select_subbrand(subbrand):
    if subbrand not in sub_brand_mapping:
        raise ValueError(
            f"Sub-brand '{subbrand}' is not available. Please choose from this list: {list(sub_brand_mapping.keys())}.")

    subbrand_keywords = sub_brand_mapping[subbrand]

    # Case: multiple keyword lists for a sub-brand (e.g., Yoga, Tablet)
    if isinstance(subbrand_keywords[0], list):
        extract_parts = []
        for i, keywords_group in enumerate(subbrand_keywords):
            print(f"🔍 Extracting part {i+1} for sub-brand: {subbrand}")
            extract = extract_google_trends_data(keywords_group)
            extract_parts.append(extract)

        # Special handling: additional keywords for Yoga only in Japan
        if subbrand == "Yoga":
            yoga_jp = ["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "NEC LAVIE", "HP ENVY"]
            japan_only = {"JP": "Japan"}
            print("🌏 Extracting Yoga-specific keywords for Japan (yoga_jp)...")
            extract_japan = extract_google_trends_data(yoga_jp, countries_subset=japan_only)
            extract_parts.append(extract_japan)

        # Combine all parts and drop duplicates
        final_extract = pd.concat(extract_parts, ignore_index=True)
        final_extract = final_extract.drop_duplicates(
            subset=["Day", "Country", "Region", "Search term"],
            keep='first'
        )

    else:
        # Single group of keywords
        print(f"🔍 Extracting sub-brand: {subbrand}")
        final_extract = extract_google_trends_data(subbrand_keywords)

    return final_extract

print("=== Memulai Mengekstrak Data Google Trends ===")
brand_name = input("\nSelect which Lenovo sub brand you want to extract (example: 'legion', 'ideapad', etc): ").lower()
Google_trend_name = input("Type file name for extracted google trends data (example: 'result_google_trends.xlsx'): ")
if not Google_trend_name.endswith('.xlsx'):
        Google_trend_name = Google_trend_name + '.xlsx'


all_data = select_subbrand(brand_name)
output_path = "D:/Python/Lenovo Google Trend - Copy/Raw_file/"  + Google_trend_name
print(all_data.head(10))
print(f"Berikut adalah negara yang telah diekstrak: {all_data['Country'].unique()}")
print(f"Berikut adalah region yang telah diekstrak: {all_data['Region'].unique()}")
print(f"Berikut adalah search term yang telah diekstrak: {all_data['Search term'].unique()}")
print(all_data.shape)
print(type(all_data))

# Save the combined data to an Excel file
with pd.ExcelWriter(output_path) as writer:
    all_data.to_excel(writer, index=False)

print(f"📁 Extraction process completed, data has been saved in: {output_path}")