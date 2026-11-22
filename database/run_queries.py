
import sqlite3
from pathlib import Path

# Locate database
SCRIPT_DIR = Path(__file__).resolve().parent
DATABASE_FILE = SCRIPT_DIR / "retail_business.db"

# Connect to database
connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

print("=" * 55)
print("SQL BUSINESS ANALYSIS")
print("=" * 55)

# 1. TOTAL REVENUE
print("\n1. TOTAL REVENUE")

cursor.execute("""
    SELECT ROUND(SUM(Revenue), 2)
    FROM sales
""")

print("Total Revenue: £", cursor.fetchone()[0])


# 2. TOTAL ORDERS
print("\n2. TOTAL ORDERS")

cursor.execute("""
    SELECT COUNT(DISTINCT InvoiceNo)
    FROM sales
""")

print("Total Orders:", cursor.fetchone()[0])


# 3. MONTHLY REVENUE
print("\n3. MONTHLY REVENUE")

cursor.execute("""
    SELECT
        SUBSTR(InvoiceDate, 1, 7) AS YearMonth,
        ROUND(SUM(Revenue), 2) AS MonthlyRevenue
    FROM sales
    GROUP BY YearMonth
    ORDER BY YearMonth
""")

for row in cursor.fetchall():
    print(row)


# 4. TOP 10 COUNTRIES
print("\n4. TOP 10 COUNTRIES")

cursor.execute("""
    SELECT
        Country,
        ROUND(SUM(Revenue), 2) AS TotalRevenue
    FROM sales
    GROUP BY Country
    ORDER BY TotalRevenue DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)


# 5. TOP 10 MERCHANDISE PRODUCTS
print("\n5. TOP 10 MERCHANDISE PRODUCTS")

cursor.execute("""
    SELECT
        Description,
        ROUND(SUM(Revenue), 2) AS TotalRevenue
    FROM sales
    WHERE UPPER(TRIM(Description)) NOT LIKE '%POSTAGE%'
      AND UPPER(TRIM(Description)) <> 'MANUAL'
    GROUP BY Description
    ORDER BY TotalRevenue DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)


# 6. TOP 10 CUSTOMERS
print("\n6. TOP 10 CUSTOMERS")

cursor.execute("""
    SELECT
        CustomerID,
        ROUND(SUM(Revenue), 2) AS TotalRevenue,
        COUNT(DISTINCT InvoiceNo) AS TotalOrders
    FROM sales
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
    ORDER BY TotalRevenue DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(row)


connection.close()

print("\nSQL BUSINESS ANALYSIS COMPLETED!")
