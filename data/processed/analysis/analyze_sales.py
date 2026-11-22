
import pandas as pd
from pathlib import Path

# Locate project folders
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent.parent.parent

INPUT_FILE = PROJECT_DIR / "data" / "processed" / "cleaned_sales.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed" / "eda"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load cleaned dataset
df = pd.read_csv(
    INPUT_FILE,
    dtype={"InvoiceNo": str},
    parse_dates=["InvoiceDate"],
    low_memory=False
)

print("=" * 55)
print("RETAIL BUSINESS ANALYSIS")
print("=" * 55)

# 1. KEY BUSINESS KPIs
total_revenue = df["Revenue"].sum()
total_orders = df["InvoiceNo"].nunique()
total_products = df["StockCode"].nunique()
total_customers = df["CustomerID"].nunique()
average_order_value = total_revenue / total_orders

print("\nKEY BUSINESS KPIs")
print("-" * 40)
print("Total Revenue: £", round(total_revenue, 2))
print("Total Orders:", total_orders)
print("Unique Products:", total_products)
print("Identified Customers:", total_customers)
print("Average Order Value: £", round(average_order_value, 2))

# 2. MONTHLY REVENUE
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)

monthly_revenue = (
    df.groupby("YearMonth")["Revenue"]
    .sum()
    .reset_index()
    .sort_values("YearMonth")
)

monthly_revenue.to_csv(
    OUTPUT_DIR / "monthly_revenue.csv", index=False
)

print("\nMONTHLY REVENUE")
print(monthly_revenue.to_string(index=False))

# 3. COUNTRY PERFORMANCE
country_revenue = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

country_revenue.to_csv(
    OUTPUT_DIR / "country_revenue.csv", index=False
)

print("\nTOP 10 COUNTRIES")
print(country_revenue.head(10).to_string(index=False))

# 4. TOP 10 PRODUCTS BY REVENUE
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

top_products.to_csv(
    OUTPUT_DIR / "top_products.csv", index=False
)

print("\nTOP 10 PRODUCTS")
print(top_products.to_string(index=False))

# 5. CUSTOMER PERFORMANCE
customer_data = df.dropna(subset=["CustomerID"])

customer_summary = (
    customer_data.groupby("CustomerID")
    .agg(
        Total_Revenue=("Revenue", "sum"),
        Total_Orders=("InvoiceNo", "nunique"),
        Total_Quantity=("Quantity", "sum")
    )
    .reset_index()
    .sort_values("Total_Revenue", ascending=False)
)

customer_summary.to_csv(
    OUTPUT_DIR / "customer_summary.csv", index=False
)

print("\nTOP 10 CUSTOMERS")
print(customer_summary.head(10).to_string(index=False))

print("\nEDA FILES SAVED TO:")
print(OUTPUT_DIR)

print("\nBUSINESS ANALYSIS COMPLETED!")
