
import pandas as pd
import os

file_path = "Online Retail.xlsx"

if not os.path.exists(file_path):
    print("ERROR: Dataset not found!")
else:
    df = pd.read_excel(file_path)

    print("\n========== DATASET OVERVIEW ==========")
    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nDataset Information:")
    df.info()

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Records:")
    print(df.duplicated().sum())

    print("\nBasic Statistics:")
    print(df.describe(include="all"))