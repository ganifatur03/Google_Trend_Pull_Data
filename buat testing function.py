from client import RestClient
import pandas as pd

data = pd.read_excel("D:/Python/Lenovo Google Trend - Copy/test_file/loq-youtube-com.xlsx", engine='openpyxl')

# Drop data 2021
data = data[data['Week'].dt.year != 2021]

print(data.head(10))