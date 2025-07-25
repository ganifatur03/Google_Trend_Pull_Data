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
    'NZ': "New Zealand",
    'WORLD': None  # Worldwide
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
    "Worldwide": "WW"
}


# Dictionary of Keywords group for each brand
sub_brand_mapping = {
    "yoga": [["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY"], 
             ["LENOVO YOGA", "APPLE MACBOOK", "DELL INSPIRON 7000", "ACER SWIFT", "HP SPECTRE"]],
    "ideapad": ["LENOVO IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"] ,
    "loq": ["LENOVO LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "legion": ["LENOVO LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "handheld": ["LEGION GO", "MSI CLAW", "ROG ALLY", "STEAM DECK"],
    "brand": ["LENOVO"],
    "yoga_testing1": ["LENOVO YOGA", "APPLE MACBOOK", "ACER SPIN"],
    "yoga_testing2": ["LENOVO YOGA", "ACER SPIN", "DELL INSPIRON 7000", "ACER SWIFT", "HP SPECTRE"],
    "keyword_test" : ["LENOVO YOGA", "Dell Plus", "Dell Premium", "HP OmniBook Ultra", "HP OmniBook X"]
}

# Date range for Google Trends data
date_from = "2022-01-01"
date_to = "2025-06-30"

# List to store all Google Trend result API data
data_trend_list = []

# Function to extract Google Trends data while also loop it through countries
def extract_google_trends_data(keywords_group, countries_subset=None):
    selected_countries = countries_subset if countries_subset is not None else countries

    for code, country in selected_countries.items():
        post_data = {
            0: {
                "location_name": country,
                "date_from": date_from,
                "date_to": date_to,
                "type": "youtube",
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
                    row = {"Week": date_str}
                    for i, kw in enumerate(keywords_group):
                        row[f"{kw}: ({country})"] = values[i]
                    rows.append(row)

                df = pd.DataFrame(rows)

                # Add Country and Region columns
                if country is None:
                    df['Country'] = "Worldwide"
                    df['Region'] = "WW"
                else:
                    region = region_mapping.get(country, "Unknown")
                    df['Country'] = country
                    df['Region'] = region


                # Clean column names by removing ": (country)"
                df.columns = df.columns.str.replace(r":\s*\(.+?\)", "", regex=True)

                # Parse Week column
                try:
                    df['Week'] = pd.to_datetime(df['Week'], format='%d/%m/%Y')
                except:
                    try:
                        df['Week'] = pd.to_datetime(df['Week'])
                    except:
                        print(f"Date parsing issue for {country}. Please check the date format.")
                        continue
                df['Week'] = df['Week'].dt.date  # Keep only the date part

                # Convert Google Trend data to long format
                data_trend = df.melt(
                    id_vars=['Week', 'Country', 'Region'],
                    var_name='Search term',
                    value_name='Trend index'
                )

                data_trend_list.append(data_trend)
                print(f"✅ Successfully extracted data for {country}")

            except Exception as e:
                print(f"⚠️ Failed to extract data for {country}: {e}")
        else:
            print(f"API error for {country}: {response['status_message']}")
    
    # Combine all data from each countries into a single DataFrame
    final_result = pd.concat(data_trend_list, ignore_index=True)
    return final_result

# Function to select which sub-brand to be extracted
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
        if subbrand == "yoga":
            yoga_jp = ["LENOVO YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "NEC LAVIE", "HP ENVY"]
            japan_only = {"JP": "Japan"}
            print("🌏 Extracting Yoga-specific keywords for Japan (yoga_jp)...")
            extract_japan = extract_google_trends_data(yoga_jp, countries_subset=japan_only)
            extract_parts.append(extract_japan)

        # Combine all parts and drop duplicates
        final_extract = pd.concat(extract_parts, ignore_index=True)
        final_extract = final_extract.drop_duplicates(
            subset=["Week", "Country", "Region", "Search term"],
            keep='first'
        )

    else:
        # Single group of keywords
        print(f"🔍 Extracting sub-brand: {subbrand}")
        final_extract = extract_google_trends_data(subbrand_keywords)

    return final_extract

# Main execution starts here, also includes user input for sub-brand and logging purpose
print("=== Begin extracting Google Trends data ===")

brand_name = input("\nSelect which Lenovo sub brand you want to extract (example: 'legion', 'ideapad', etc): ").lower()
Google_trend_name = input("Type the file name for extracted data (example: 'result_google_trends.xlsx'): ")
if not Google_trend_name.endswith('.xlsx'):
        Google_trend_name = Google_trend_name + '.xlsx'

all_data = select_subbrand(brand_name)
output_path = "D:/Python/Lenovo Google Trend - Copy/test_file/"  + Google_trend_name

print(all_data.head(10))
print(f"\nThis is Country name inside extracted data: {all_data['Country'].unique()}")
print(f"This is Region name inside extracted data: {all_data['Region'].unique()}")
print(f"This is Search term inside extracted data: {all_data['Search term'].unique()}")
print(all_data.shape)

# Save the combined data to an Excel file
with pd.ExcelWriter(output_path) as writer:
    all_data.to_excel(writer, index=False)

print(f"\n📁 Extraction process completed, data has been saved in: {output_path}")