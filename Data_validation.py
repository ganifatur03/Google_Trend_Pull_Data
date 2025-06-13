import pandas as pd

# --- Mapping Country to Region ---
country_region_mapping = {
    "Indonesia": "CAP", "Malaysia": "CAP", "Singapore": "CAP", "Philippines": "CAP",
    "Vietnam": "CAP", "Thailand": "CAP", "Taiwan": "CAP", "Hong Kong": "CAP",
    "South Korea": "CAP", "Japan": "JP", "India": "IN", "Australia": "ANZ",
    "New Zealand": "ANZ", "Worldwide": "WW"
}

# --- Sub-brand keywords dictionary ---
sub_brand_mapping = {
    "YOGA": ["YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY", "DELL INSPIRON 7000", "ACER SWIFT", "HP SPECTRE", "NEC LAVIE"],
    "IDEAPAD": ["IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"],
    "LOQ": ["LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "LEGION": ["LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "LEGION GO": ["LEGION GO", "MSI CLAW", "ROG ALLY", "STEAM DECK"],
    "LENOVO": "LENOVO"
}

category_mapping = {
    "Premium": ["YOGA", "APPLE MACBOOK", "ASUS ZENBOOK", "DELL XPS", "HP ENVY", "DELL INSPIRON 7000", "ACER SWIFT", "HP SPECTRE", "NEC LAVIE"],
    "Mainstream Gaming": ["LOQ", "ACER NITRO", "HP VICTUS", "MSI CYBORG", "ASUS TUF"],
    "Gaming": ["LEGION", "ASUS ROG", "HP OMEN", "ACER PREDATOR", "MSI GAMING"],
    "Handheld Gaming": ["LEGION GO", "MSI CLAW", "ROG ALLY", "STEAM DECK"],
}

blank_category_search_terms = ["LENOVO", "IDEAPAD", "HP PAVILION", "ASUS VIVOBOOK", "ACER ASPIRE", "DELL INSPIRON"]



def check_data_quality(df, required_cols):
    print("\n=====  DATA QUALITY CHECK =====")

    # 1. Check any missing/null/NaN values
    print("\n----) Checking for null or NaN values:")
    missing = df[required_cols].isnull().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        print(f"⚠️ Missing values found in:\n{missing}")
    else:
        print("✅ No missing values in required columns.")

    # 2. Check unique value and consistency of column Country & Region
    print("\n----) Checking unique countries and regions:")
    print("Unique Countries:", df['Country'].dropna().unique())
    print("Unique Regions :", df['Region'].dropna().unique())

    # 3. Check unique value and validate column for Search term
    print("\n----) Checking 'Search term' values:")
    print(df['Search term'].value_counts())

    print("\n✅ Data quality check complete.")

def validate_search_term_competitor(df, mapping, search_col="Search term", competitor_col="Lenovo & Competitor", allowed_blank_terms=None):
    print(f"\n===== VALIDATING {search_col} vs {competitor_col} =====")

    if allowed_blank_terms is None:
        allowed_blank_terms = []

    invalid_rows = []

    for idx, row in df.iterrows():
        search_term = str(row[search_col]).strip().upper()
        competitor = str(row[competitor_col]).strip().upper()

        # Allow blank competitor for certain search terms
        if search_term in [t.upper() for t in allowed_blank_terms] and competitor in ["", "NAN", "NONE"]:
            continue
        
        # Check if search term exists in mapping
        found = False
        for group, terms in mapping.items():
            if search_term in [t.upper() for t in terms]:
                found = True
                if competitor != group.upper():
                    invalid_rows.append((idx, search_term, competitor, group))
                break

        if not found:
            invalid_rows.append((idx, search_term, competitor, "Unknown group"))

    if invalid_rows:
        print("⚠️ Found mismatched rows:")
        for row in invalid_rows:
            print(f"Row {row[0]}: {search_col} '{row[1]}' was recorded as '{row[2]}'. It supposed to be classified as '{row[3]}'")
    else:
        print("✅ All search term-competitor pairs are valid.")


def validate_country_region(df, expected_mapping):
    print("\n===== COUNTRY & REGION VALIDATION =====")

    actual_countries = set(df['Country'].dropna().unique())
    expected_countries = set(expected_mapping.keys())

    missing = expected_countries - actual_countries
    unexpected = actual_countries - expected_countries

    if missing:
        print(f"⚠️ Missing countries in data: {missing}")
    else:
        print("✅ All expected countries are present.")

    if unexpected:
        print(f"❌ Unexpected/typo countries found: {unexpected}")

    # Validate region correctness
    wrong_region = []
    for country, expected_region in expected_mapping.items():
        region_in_df = df[df['Country'] == country]['Region'].unique()
        if len(region_in_df) > 0 and expected_region not in region_in_df:
            wrong_region.append((country, list(region_in_df)))

    if wrong_region:
        print(f"⚠️ Region mismatch found for: {wrong_region}")
    else:
        print("✅ All country-region combinations are valid.")


def validate_search_terms(df, subbrand_map):
    print("\n==== SEARCH TERM VALIDATION ====")

    # Flatten all search terms from sub-brand mapping
    expected_terms = set()
    for val in subbrand_map.values():
        if isinstance(val, list):
            for group in val:
                if isinstance(group, list):
                    expected_terms.update(group)
                else:
                    expected_terms.add(group)

    found_terms = set(df['Search term'].dropna().unique())

    missing_terms = expected_terms - found_terms
    unexpected_terms = found_terms - expected_terms

    if missing_terms:
        print(f"⚠️ Missing search terms: {missing_terms}")
    else:
        print("✅ All expected search terms are found.")

    if unexpected_terms:
        print(f"❌ Unexpected terms found (possibly typos): {unexpected_terms}")

# --- MAIN FUNCTION ---
def main():
    # 1. File input
    print("===== Data Validation Tool =====")
    print("\nThis tool will help you validate your Google Trends data file.")
    file_name = input("📂 Enter file name (CSV or Excel): ").strip()
    file_path = "D:/Python/Lenovo Google Trend - Copy/test_file/" + file_name

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Failed to load file: {e}")
        return

    # 2. Info dasar
    print(f"---) Loaded data shape: {df.shape}")
    print(f"---) Columns in file:\n{list(df.columns)}")

    # 3. Input kolom yang mau diuji
    exclude_input = input("\nEnter column names to exclude (comma-separated, or press Enter to keep all): ").strip()

    if exclude_input == "":
        exclude_cols = []
        print("\nNo columns excluded. All columns are selected.")
    else:
        exclude_cols = [col.strip() for col in exclude_input.split(',') if col.strip() in df.columns]

    selected_cols = [col for col in df.columns if col not in exclude_cols]
    df_filtered = df[selected_cols]

    # 4. Jalankan validasi
    check_data_quality(df_filtered, selected_cols)

    validate_search_term_competitor(df, sub_brand_mapping)

    validate_search_term_competitor(df, category_mapping, 
                                    competitor_col="Premium & Gaming", allowed_blank_terms=blank_category_search_terms)

    validate_country_region(df_filtered, country_region_mapping)

    validate_search_terms(df_filtered, sub_brand_mapping)

if __name__ == "__main__":
    main()
