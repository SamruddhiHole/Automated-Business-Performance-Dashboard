
import pandas as pd
import sqlite3
from pathlib import Path

# 1. Locate project folders
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

# 2. Define file paths
INPUT_FILE = PROJECT_DIR / "data" / "processed" / "cleaned_sales.csv"
DATABASE_FILE = SCRIPT_DIR / "retail_business.db"

print("=" * 55)
print("RETAIL DATABASE CREATION")
print("=" * 55)

# 3. Load cleaned sales data
print("\nLoading cleaned sales data...")

df = pd.read_csv(
    INPUT_FILE,
    dtype={"InvoiceNo": str},
    low_memory=False
)

print("Records loaded:", len(df))

# 4. Connect to SQLite database
print("\nConnecting to SQLite database...")

connection = sqlite3.connect(DATABASE_FILE)

# 5. Import data into a SQL table
print("\nImporting records into database...")

df.to_sql(
    "sales",
    connection,
    if_exists="replace",
    index=False
)

# 6. Create indexes for faster queries
print("\nCreating database indexes...")

connection.execute(
    'CREATE INDEX IF NOT EXISTS idx_invoice ON sales (InvoiceNo)'
)

connection.execute(
    'CREATE INDEX IF NOT EXISTS idx_country ON sales (Country)'
)

connection.execute(
    'CREATE INDEX IF NOT EXISTS idx_customer ON sales (CustomerID)'
)

connection.execute(
    'CREATE INDEX IF NOT EXISTS idx_date ON sales (InvoiceDate)'
)

connection.commit()

# 7. Verify database
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM sales")
record_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT InvoiceNo) FROM sales")
order_count = cursor.fetchone()[0]

# 8. Display report
print("\nDATABASE VERIFICATION")
print("-" * 40)

print("Records in database:", record_count)
print("Unique orders:", order_count)
print("Database location:", DATABASE_FILE)

connection.close()

print("\nDATABASE CREATED SUCCESSFULLY!")
