from client import RestClient
import pandas as pd

Login_email = "gani@team.superfk.co"
Login_password = "f881f3d369097a8a"
# Initialize client
client = RestClient(Login_email, Login_password)

post_data = dict()

# Menambahkan 1 task untuk Google Trends Indonesia, Maret 2025, Web Search
post_data[len(post_data)] = dict(
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

# Mengirim permintaan ke endpoint live Google Trends Explore
response = client.post("/v3/keywords_data/google_trends/explore/live", post_data)

# Cek hasil respons
if response["status_code"] == 20000:
    print(response)
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


