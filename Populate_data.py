import pandas as pd
from glob import glob
import numpy as np
import os

sos_folder = "D:/Data work/Lenovo/Raw Data/04. Share of Search (new)/Computer Category"

# Search for all Excel files in the specified folder and its subfolders
excel_files = glob(os.path.join(sos_folder, "*", "*.xlsx"))

# List to hold all DataFrames
all_dataframes = []

# Loop through all files and read into DataFrames
for file in excel_files:
    try:
        df = pd.read_excel(file, engine="openpyxl")
        df['source_file'] = os.path.basename(file)  # Add filename
        df['source_folder'] = os.path.basename(os.path.dirname(file))  # Add folder name
        all_dataframes.append(df)
    except Exception as e:
        print(f"Error processing {file}: {e}")

# Combine all DataFrames if any were loaded
if all_dataframes:
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"Combined dataframe has shape such as: {combined_df.shape}")
else:
    print("No data was loaded. Check the path and file patterns.")

print(combined_df.head(10))

# Function to clean and process the Share of Search data
def clean_share_of_search_data(t_df):
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
    t_df['Year'] = t_df['Week'].dt.year
    t_df['Month.no'] = t_df['Week'].dt.month
    t_df['Month Name'] = t_df['Month.no'].map(month_dict)
    t_df['Quarter'] = 'Q' + t_df['Week'].dt.quarter.astype(str)
    t_df['MMM'] = t_df['Month Name'].str[:3]
    t_df['Quarter (SOS)'] = t_df['Quarter'] + ' FY' + t_df['Year'].astype(str)
    search_rename = {
        'LENOVO IDEAPAD': 'IDEAPAD',
        'LENOVO LEGION': 'LEGION',
        'LENOVO YOGA': 'YOGA',
        'LENOVO LOQ': 'LOQ',
        'LENOVO TABLET': 'TABLET',
        'LENOVO TAB': 'TAB',
        'ACER INSPIRE': 'ACER ASPIRE',  # Correcting typo
        'APLLE IPAD': 'APPLE IPAD'  # Correcting typo
    }

    t_df['Search term'] = t_df['Search term'].replace(search_rename)

    search_mapping = {
        'ACER ASPIRE': {'premium&gaming':np.nan, 'brand': 'ACER', 'lenovo&competitor': 'IDEAPAD'},
        'ACER NITRO': {'premium&gaming':'Mainstream Gaming', 'brand': 'ACER', 'lenovo&competitor': 'LOQ'},
        'ACER PREDATOR': {'premium&gaming':'Gaming', 'brand': 'ACER', 'lenovo&competitor': 'LEGION'},
        'ACER SWIFT': {'premium&gaming':'Premium', 'brand': 'ACER', 'lenovo&competitor': 'YOGA'},
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
        'YOGA': {'premium&gaming':'Premium', 'brand': 'LENOVO', 'lenovo&competitor': 'YOGA'}
    }
    # Map premium&gaming
    t_df['Premium & Gaming'] = t_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('premium&gaming'))

    # Map brand
    t_df['Brand'] = t_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('brand'))

    # Map lenovo&competitor
    t_df['Lenovo & Competitor'] = t_df['Search term'].map(lambda x: search_mapping.get(x, {}).get('lenovo&competitor'))

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
    t_df['Country'] = t_df['Country'].replace(country_mapping)
    t_df['Week'] = t_df['Week'].dt.date

    t_df['Merge'] = t_df['Quarter (SOS)'] + ' ' + t_df['Country'] + ' ' + t_df['Search term']
    t_df = t_df[['Week', 'Country', 'Region', 'Search term', 'Trend index', 'Brand',
        'Premium & Gaming', 'Year', 'Month Name', 'Month.no', 'Quarter', 'MMM',
        'Quarter (SOS)', 'Merge', 'Lenovo & Competitor']]
    
    return t_df

t_df = clean_share_of_search_data(combined_df)

print(f"Processed DataFrame has shape such as: {t_df.shape}")
print(t_df.head(10))

# Save the cleaned DataFrame to a new Excel file
#t_df.to_csv("sos_processed_yearly_world(9jun).csv", index=False)