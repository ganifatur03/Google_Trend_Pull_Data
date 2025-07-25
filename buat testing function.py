import pandas as pd

# Define the folder containing the Share of Search Excel Raw files
folder_available = ["computer", "youtube"]
select_folder = input("Please input the folder path: (Chose Computer / Youtube )\n").lower()

if select_folder not in folder_available:
    raise ValueError(f"Invalid folder selected. Please choose from: {folder_available}")

path = "D:/Data work/Lenovo/Raw Data/04. Share of Search (new)/"
share_of_search_folder = path + select_folder + " data"
print(f"Selected folder: {share_of_search_folder}")
