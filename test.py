from client import RestClient
import pandas as pd
from datetime import datetime

Login_email = "gani@team.superfk.co"
Login_password = "f881f3d369097a8a"
# Initialize client
client = RestClient(Login_email, Login_password)

post_data = dict()

# Request data Google Trends
post_data[0] = dict(
    location_name="Indonesia",
    date_from="2025-03-01",
    date_to="2025-03-31",
    type="web",
    keywords=[
        "LENOVO LEGION",
        "ASUS ROG",
        "HP OMEN",
        "ACER PREDATOR",
        "MSI GAMING"
    ]
)

response = client.post("/v3/keywords_data/google_trends/explore/live", post_data)

if response["status_code"] == 20000:
    # Ambil data
    result = response["tasks"][0]["result"][0]
    keywords = result["keywords"]
    trend_data = result["items"][0]["data"]

    # Siapkan list data baris
    rows = []

    for entry in trend_data:
        date_str = datetime.strptime(entry["date_from"], "%Y-%m-%d").strftime("%d/%m/%Y")
        values = [v if v is not None else 0 for v in entry["values"]]
        row = {"Day": date_str}
        for i, keyword in enumerate(keywords):
            row[keyword + ": (Indonesia)"] = values[i]
        rows.append(row)

    # Konversi ke DataFrame dan simpan ke Excel
    df = pd.DataFrame(rows)
    df.to_excel("D:/Python/Lenovo Google Trend/testing.xlsx", index=False)

    print("✅ Data berhasil disimpan dalam format pivot ke testing.xlsx")

else:
    print(f"❌ Error. Code: {response['status_code']} Message: {response['status_message']}")



