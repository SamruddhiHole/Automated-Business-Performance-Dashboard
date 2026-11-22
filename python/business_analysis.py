"""
Business Analysis & Reporting Module.

Executes automated retail business performance analytics across financial, order,
product, country, and customer dimensions. Generates all standardized summary
CSV reports for downstream reporting and Power BI visualization.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from python.database_manager import DatabaseManager


def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates high-level executive business KPIs.

    Args:
        df: Cleaned sales DataFrame.

    Returns:
        Dictionary of key metrics.
    """
    total_revenue = float(round(df["Revenue"].sum(), 2))
    total_orders = int(df["InvoiceNo"].nunique())
    unique_products = int(df["StockCode"].nunique())
    identified_customers = int(df["CustomerID"].dropna().nunique())
    total_quantity = int(df["Quantity"].sum())
    aov = float(round(total_revenue / total_orders, 2)) if total_orders > 0 else 0.0

    dates = pd.to_datetime(df["InvoiceDate"])
    date_min = str(dates.min()) if not dates.empty else ""
    date_max = str(dates.max()) if not dates.empty else ""

    return {
        "Total_Revenue": total_revenue,
        "Total_Orders": total_orders,
        "Identified_Customers": identified_customers,
        "Unique_Products": unique_products,
        "Average_Order_Value": aov,
        "Total_Quantity_Sold": total_quantity,
        "Date_Range_Start": date_min,
        "Date_Range_End": date_max,
    }


def generate_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates monthly revenue, orders, quantity, and AOV trends."""
    df_temp = df.copy()
    df_temp["YearMonth"] = pd.to_datetime(df_temp["InvoiceDate"]).dt.to_period("M").astype(str)

    monthly = (
        df_temp.groupby("YearMonth")
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("InvoiceNo", "nunique"),
            Total_Quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("YearMonth")
    )
    monthly["Total_Revenue"] = monthly["Total_Revenue"].round(2)
    monthly["Average_Order_Value"] = (monthly["Total_Revenue"] / monthly["Total_Orders"]).round(2)

    return monthly


def generate_country_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates revenue breakdown by country with market share percentage."""
    total_rev = df["Revenue"].sum()
    country = (
        df.groupby("Country")
        .agg(
            Total_Revenue=("Revenue", "sum"),
            Total_Orders=("InvoiceNo", "nunique"),
            Customer_Count=("CustomerID", lambda x: x.dropna().nunique()),
            Total_Quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("Total_Revenue", ascending=False)
    )
    country["Total_Revenue"] = country["Total_Revenue"].round(2)
    country["Revenue_Share_Pct"] = ((country["Total_Revenue"] / total_rev) * 100).round(2)

    return country


def generate_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates product performance rankings, excluding postage and non-merchandise fees."""
    # Filter out non-merchandise items
    desc_upper = df["Description"].astype(str).str.upper().str.strip()
    is_postage = desc_upper.str.contains("POSTAGE", na=False) | desc_upper.str.contains(r"\bPOST\b", na=False, regex=True)
    is_fee = desc_upper.isin(["MANUAL", "DISCOUNT", "BANK CHARGES", "AMAZON FEE", "SAMPLES"])

    merchandise_df = df[~(is_postage | is_fee)].copy()

    products = (
        merchandise_df.groupby(["StockCode", "Description"])
        .agg(
            Total_Quantity_Sold=("Quantity", "sum"),
            Total_Revenue=("Revenue", "sum"),
            Avg_Unit_Price=("UnitPrice", "mean"),
        )
        .reset_index()
        .sort_values("Total_Revenue", ascending=False)
    )
    products["Total_Revenue"] = products["Total_Revenue"].round(2)
    products["Avg_Unit_Price"] = products["Avg_Unit_Price"].round(2)

    return products


def generate_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates customer spend and order frequency, excluding missing CustomerIDs."""
    cust_df = df.dropna(subset=["CustomerID"]).copy()

    customers = (
        cust_df.groupby("CustomerID")
        .agg(
            Country=("Country", "first"),
            Total_Orders=("InvoiceNo", "nunique"),
            Total_Quantity=("Quantity", "sum"),
            Total_Spend=("Revenue", "sum"),
        )
        .reset_index()
        .sort_values("Total_Spend", ascending=False)
    )
    customers["Total_Spend"] = customers["Total_Spend"].round(2)
    customers["Avg_Order_Spend"] = (customers["Total_Spend"] / customers["Total_Orders"]).round(2)

    return customers


def run_all_business_analyses(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Generates all business performance summaries and exports them to reports/ and data/processed/eda/.

    Args:
        df: Cleaned sales DataFrame.

    Returns:
        Dictionary of summary DataFrames.
    """
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    config.EDA_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Executive KPIs
    kpis = calculate_executive_kpis(df)
    kpi_records = [{"Metric": k, "Value": v} for k, v in kpis.items()]
    df_kpi = pd.DataFrame(kpi_records)
    df_kpi.to_csv(config.BUSINESS_SUMMARY, index=False)

    # 2. Monthly Summary
    monthly = generate_monthly_summary(df)
    monthly.to_csv(config.MONTHLY_SALES_SUMMARY, index=False)
    # Also save to legacy eda location for existing visual compatibility
    monthly[["YearMonth", "Total_Revenue"]].rename(columns={"Total_Revenue": "Revenue"}).to_csv(
        config.EDA_DATA_DIR / "monthly_revenue.csv", index=False
    )

    # 3. Country Summary
    country = generate_country_summary(df)
    country.to_csv(config.COUNTRY_SALES_SUMMARY, index=False)
    # Also save to legacy eda location
    country[["Country", "Total_Revenue"]].rename(columns={"Total_Revenue": "Revenue"}).to_csv(
        config.EDA_DATA_DIR / "country_revenue.csv", index=False
    )

    # 4. Product Summary
    products = generate_product_summary(df)
    products.to_csv(config.PRODUCT_SALES_SUMMARY, index=False)
    # Also save top products to legacy eda location
    products.head(10)[["Description", "Total_Revenue"]].rename(columns={"Total_Revenue": "Revenue"}).to_csv(
        config.EDA_DATA_DIR / "top_products.csv", index=False
    )

    # 5. Customer Summary
    customers = generate_customer_summary(df)
    customers.to_csv(config.CUSTOMER_SALES_SUMMARY, index=False)
    # Also save to legacy eda location
    customers.rename(columns={"Total_Spend": "Total_Revenue"})[
        ["CustomerID", "Total_Revenue", "Total_Orders", "Total_Quantity"]
    ].to_csv(config.EDA_DATA_DIR / "customer_summary.csv", index=False)

    return {
        "kpi": df_kpi,
        "monthly": monthly,
        "country": country,
        "product": products,
        "customer": customers,
    }


if __name__ == "__main__":
    if config.CLEANED_SALES_CSV.exists():
        print(f"Loading: {config.CLEANED_SALES_CSV} ...")
        df_sales = pd.read_csv(config.CLEANED_SALES_CSV, dtype={"InvoiceNo": str}, low_memory=False)
        summaries = run_all_business_analyses(df_sales)
        print("\nExecutive Business KPIs:")
        print(summaries["kpi"].to_string(index=False))
        print(f"\nAll reports generated successfully in: {config.REPORTS_DIR}")
    else:
        print("[-] Cleaned sales dataset not found.")
