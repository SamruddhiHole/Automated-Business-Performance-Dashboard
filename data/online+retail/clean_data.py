
import pandas as pd
from pathlib import Path

# Locate project and dataset
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent

INPUT_FILE = SCRIPT_DIR / "Online Retail.xlsx"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load original dataset
df = pd.read_excel(INPUT_FILE)

print("=" * 55)
print("RETAIL DATA CLEANING")
print("=" * 55)

original_rows = len(df)

# 1. Remove exact duplicate records
df = df.drop_duplicates().copy()
duplicates_removed = original_rows - len(df)

# 2. Identify cancelled invoices
cancelled = df["InvoiceNo"].astype(str).str.startswith("C", na=False)

# 3. Separate non-standard transactions
non_sales_mask = (
    cancelled
    | (df["Quantity"] <= 0)
    | (df["UnitPrice"] <= 0)
)

non_sales = df[non_sales_mask].copy()

# 4. Keep valid sales transactions
sales = df[~non_sales_mask].copy()

# 5. Handle missing product descriptions
sales["Description"] = sales["Description"].fillna(
    "Unknown Product"
)

# 6. Convert invoice date to datetime
sales["InvoiceDate"] = pd.to_datetime(
    sales["InvoiceDate"], errors="coerce"
)

# Remove records with invalid dates
sales = sales.dropna(subset=["InvoiceDate"])

# 7. Calculate revenue
sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]

# 8. Convert CustomerID to nullable integer
sales["CustomerID"] = sales["CustomerID"].astype("Int64")

# 9. Save processed datasets
sales.to_csv(
    OUTPUT_DIR / "cleaned_sales.csv",
    index=False
)

non_sales.to_csv(
    OUTPUT_DIR / "non_sales_transactions.csv",
    index=False
)

# 10. Display cleaning report
print("\nCLEANING REPORT")
print("-" * 40)

print("Original records:", original_rows)
print("Duplicates removed:", duplicates_removed)
print("Records after deduplication:", len(df))
print("Non-standard transactions:", len(non_sales))
print("Valid sales records:", len(sales))
print("Missing Customer IDs retained:",
      sales["CustomerID"].isna().sum())
print("Missing descriptions remaining:",
      sales["Description"].isna().sum())

print("\nTotal Revenue:",
      round(sales["Revenue"].sum(), 2))

print("\nDate Range:")
print(sales["InvoiceDate"].min())
print(sales["InvoiceDate"].max())

print("\nOutput Location:")
print(OUTPUT_DIR)

print("\nCLEANING COMPLETED SUCCESSFULLY!")
