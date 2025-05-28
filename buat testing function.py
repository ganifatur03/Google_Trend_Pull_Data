import data_processing
import pandas as pd

google_trends_file = input("Masukkan path file Google Trends (misal: 'data/google_trends.xlsx'): ")
hasil = data_processing.process_trends_data(google_trends_file)

print("\nProses selesai! Berikut adalah preview hasil akhir:\n")
print(hasil.head(10))