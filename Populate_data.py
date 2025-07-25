import pandas as pd
from glob import glob
import numpy as np
import os

# Define the folder containing the Share of Search Excel Raw files
folder_available = ["computer", "youtube"]
select_folder = input("Please input the folder path: (Chose Computer / Youtube )\n").lower()

if select_folder not in folder_available:
    raise ValueError(f"Invalid folder selected. Please choose from: {folder_available}")

path = "D:/Data work/Lenovo/Raw Data/04. Share of Search (new)/"
share_of_search_folder = path + select_folder + " data"

# Search for all Excel files in the specified folder and its subfolders
excel_files = glob(os.path.join(share_of_search_folder, "*.xlsx"))

# List to hold all DataFrames
all_dataframes = []

# Loop through all files and read into DataFrames
for file in excel_files:
    try:
        df = pd.read_excel(file, engine="openpyxl")
        df['source_file'] = os.path.basename(file) 
        df['source_folder'] = os.path.basename(os.path.dirname(file)) 
        all_dataframes.append(df)
    except Exception as e:
        print(f"Error processing {file}: {e}")

# Combine all DataFrames if any were loaded
if all_dataframes:
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"Combined dataframe has shape such as: {combined_df.shape}")
else:
    print("No data was loaded. Check the path and file patterns.")

# Drop 2021 data
combined_df = combined_df[combined_df['Week'].dt.year != 2021]

#print(combined_df.head(10))

# Function to clean and process the Share of Search data
def clean_share_of_search_data(sos_df):
    month_dict = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    sos_df['Year'] = sos_df['Week'].dt.year
    sos_df['Month.no'] = sos_df['Week'].dt.month
    sos_df['Month Name'] = sos_df['Month.no'].map(month_dict)
    sos_df['Quarter'] = 'Q' + sos_df['Week'].dt.quarter.astype(str)
    sos_df['MMM'] = sos_df['Month Name'].str[:3]
    sos_df['Quarter (SOS)'] = sos_df['Quarter'] + ' FY' + sos_df['Year'].astype(str)
    search_rename = {
        'LENOVO IDEAPAD': 'IDEAPAD',
        'LENOVO LEGION': 'LEGION',
        'LENOVO YOGA': 'YOGA',
        'LENOVO LOQ': 'LOQ',
        'LENOVO TABLET': 'TABLET',
        'LENOVO TAB': 'TAB'
    }

    sos_df['Search term'] = sos_df['Search term'].replace(search_rename)

    search_mapping = {
        'ACER ASPIRE': {'premium&gaming':np.nan, 'brand': 'ACER', 'lenovo&competitor': 'IDEAPAD'},
        'ACER NITRO': {'premium&gaming':'Mainstream Gaming', 'brand': 'ACER', 'lenovo&competitor': 'LOQ'},
        'ACER PREDATOR': {'premium&gaming':'Gaming', 'brand': 'ACER', 'lenovo&competitor': 'LEGION'},
        'ACER SWIFT': {'premium&gaming':'Premium', 'brand': 'ACER', 'lenovo&competitor': 'YOGA'},
        'ACER SPIN': {'premium&gaming':'Premium', 'brand': 'ACER', 'lenovo&competitor': 'YOGA'},
        'APPLE IPAD': {'premium&gaming':np.nan, 'brand': 'APPLE', 'lenovo&competitor': 'TAB/TABLET'},
        'APPLE MACBOOK': {'premium&gaming':'Premium', 'brand': 'APPLE', 'lenovo&competitor': 'YOGA'},
        'ASUS ROG': {'premium&gaming':'Gaming', 'brand': 'ASUS', 'lenovo&competitor': 'LEGION'},
        'ASUS TUF': {'premium&gaming':'Mainstream Gaming', 'brand': 'ASUS', 'lenovo&competitor': 'LOQ'},
        'ASUS VIVOBOOK': {'premium&gaming':np.nan, 'brand': 'ASUS', 'lenovo&competitor': 'IDEAPAD'},
        'ASUS ZENBOOK': {'premium&gaming':'Premium', 'brand': 'ASUS', 'lenovo&competitor': 'YOGA'},
        'DELL INSPIRON': {'premium&gaming':np.nan, 'brand': 'DELL', 'lenovo&competitor': 'IDEAPAD'},
        'DELL INSPIRON 7000': {'premium&gaming':'Premium', 'brand': 'DELL', 'lenovo&competitor': 'YOGA'},
        'DELL XPS': {'premium&gaming':'Premium', 'brand': 'DELL', 'lenovo&competitor': 'YOGA'},
        'HP ENVY': {'premium&gaming':'Premium', 'brand': 'HP', 'lenovo&competitor': 'YOGA'},
        'HP OMEN': {'premium&gaming':'Gaming', 'brand': 'HP', 'lenovo&competitor': 'LEGION'},
        'HP PAVILION': {'premium&gaming':np.nan, 'brand': 'HP', 'lenovo&competitor': 'IDEAPAD'},
        'HP SPECTRE': {'premium&gaming':'Premium', 'brand': 'HP', 'lenovo&competitor': 'YOGA'},
        'HP VICTUS': {'premium&gaming':'Mainstream Gaming', 'brand': 'HP', 'lenovo&competitor': 'LOQ'},
        'HUAWEI MATEBOOK': {'premium&gaming':np.nan, 'brand': 'HUAWEI', 'lenovo&competitor': 'IDEAPAD'},
        'HUAWEI MATEPAD': {'premium&gaming':np.nan, 'brand': 'HUAWEI', 'lenovo&competitor': 'TAB/TABLET'},
        'IDEAPAD': {'premium&gaming':np.nan, 'brand': 'LENOVO', 'lenovo&competitor': 'IDEAPAD'},
        'LEGION': {'premium&gaming':'Gaming', 'brand': 'LENOVO', 'lenovo&competitor': 'LEGION'},
        'LENOVO': {'premium&gaming':np.nan, 'brand': 'LENOVO', 'lenovo&competitor': 'LENOVO'},
        'LOQ': {'premium&gaming':'Mainstream Gaming', 'brand': 'LENOVO', 'lenovo&competitor': 'LOQ'},
        'MSI CYBORG': {'premium&gaming':'Mainstream Gaming', 'brand': 'MSI', 'lenovo&competitor': 'LOQ'},
        'MSI GAMING': {'premium&gaming':'Gaming', 'brand': 'MSI', 'lenovo&competitor': 'LEGION'},
        'NEC LAVIE': {'premium&gaming':'Premium', 'brand': 'NEC', 'lenovo&competitor': 'YOGA'},
        'REALME PAD': {'premium&gaming':np.nan, 'brand': 'REALME', 'lenovo&competitor': 'TAB/TABLET'},
        'SAMSUNG GALAXY TAB': {'premium&gaming':np.nan, 'brand': 'SAMSUNG', 'lenovo&competitor': 'TAB/TABLET'},
        'TAB': {'premium&gaming':np.nan, 'brand': 'LENOVO', 'lenovo&competitor': 'TAB/TABLET'},
        'TABLET': {'premium&gaming':np.nan, 'brand': 'LENOVO', 'lenovo&competitor': 'TAB/TABLET'},
        'XIAOMI PAD': {'premium&gaming':np.nan, 'brand': 'XIAOMI', 'lenovo&competitor': 'TAB/TABLET'},
        'YOGA': {'premium&gaming':'Premium', 'brand': 'LENOVO', 'lenovo&competitor': 'YOGA'},
        'LEGION GO': {'premium&gaming':'Handheld Gaming', 'brand': 'LENOVO', 'lenovo&competitor': 'LEGION GO'},
        'MSI CLAW': {'premium&gaming':'Handheld Gaming', 'brand': 'MSI', 'lenovo&competitor': 'LEGION GO'},
        'ROG ALLY': {'premium&gaming':'Handheld Gaming', 'brand': 'ASUS', 'lenovo&competitor': 'LEGION GO'},
        'STEAM DECK': {'premium&gaming':'Handheld Gaming', 'brand': 'VALVE', 'lenovo&competitor': 'LEGION GO'}
    }
    # Map premium&gaming
    sos_df['Premium & Gaming'] = sos_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('premium&gaming'))

    # Map brand
    sos_df['Brand'] = sos_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('brand'))

    # Map lenovo&competitor
    sos_df['Lenovo & Competitor'] = sos_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('lenovo&competitor'))

    country_mapping = {
        'INDONESIA': 'Indonesia',
        'MALAYSIA': 'Malaysia',
        'SINGAPORE': 'Singapore',
        'PHILIPPINES': 'Philippines',
        'VIETNAM': 'Vietnam',
        'THAILAND': 'Thailand',
        'TAIWAN': 'Taiwan',
        'HONG KONG': 'Hong Kong',
        'SOUTH KOREA': 'South Korea',
        'JAPAN': 'Japan',
        'INDIA' : 'India',
        'AUSTRALIA': 'Australia',
        'NEW ZEALAND': 'New Zealand',
        'WORLDWIDE': 'Worldwide'
    }



    # Apply the mapping to standardize country names
    sos_df['Country'] = sos_df['Country'].replace(country_mapping)
    sos_df['Week'] = sos_df['Week'].dt.date

    sos_df['Merge'] = sos_df['Quarter (SOS)'] + ' ' + sos_df['Country'] + ' ' + sos_df['Search term']
    sos_df = sos_df[['Week', 'Country', 'Region', 'Search term', 'Trend index', 'Brand',
        'Premium & Gaming', 'Year', 'Month Name', 'Month.no', 'Quarter', 'MMM',
        'Quarter (SOS)', 'Merge', 'Lenovo & Competitor']]
    
    return sos_df

sos_df = clean_share_of_search_data(combined_df)

print(f"Processed DataFrame has shape such as: {sos_df.shape}")
print(sos_df.head(10))

# Save the cleaned DataFrame to a new Excel file
out_path = "D:/Python/Lenovo Google Trend - Copy/test_file/Google Trends - "
output_path = out_path + select_folder + "_data.xlsx"
with pd.ExcelWriter(output_path) as writer:
    sos_df.to_excel(writer, index=False)

print(f"\n📁 Extraction process completed, data has been saved in: {output_path}")