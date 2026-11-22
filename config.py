"""
Configuration settings for the Automated Business Performance Dashboard.

This module centralizes all project directory paths, output filenames, database
configurations, required schema definitions, and baseline reference values.
Uses pathlib for cross-platform compatibility (Windows, macOS, Linux).
"""

from pathlib import Path

# ==============================================================================
# 1. BASE DIRECTORIES
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EDA_DATA_DIR = PROCESSED_DATA_DIR / "eda"

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "retail_business.db"

REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"
POWERBI_DIR = BASE_DIR / "powerbi"
SQL_DIR = BASE_DIR / "sql"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EDA_DATA_DIR, DATABASE_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# 2. OUTPUT FILE PATHS
# ==============================================================================
CLEANED_SALES_CSV = PROCESSED_DATA_DIR / "cleaned_sales.csv"
NON_SALES_CSV = PROCESSED_DATA_DIR / "non_sales_transactions.csv"

# Summary Reports
DATA_QUALITY_REPORT = REPORTS_DIR / "data_quality_report.csv"
BUSINESS_SUMMARY = REPORTS_DIR / "business_summary.csv"
MONTHLY_SALES_SUMMARY = REPORTS_DIR / "monthly_sales_summary.csv"
COUNTRY_SALES_SUMMARY = REPORTS_DIR / "country_sales_summary.csv"
PRODUCT_SALES_SUMMARY = REPORTS_DIR / "product_sales_summary.csv"
CUSTOMER_SALES_SUMMARY = REPORTS_DIR / "customer_sales_summary.csv"
PIPELINE_RUN_SUMMARY = REPORTS_DIR / "pipeline_run_summary.txt"

# Log File
LOG_FILE = LOGS_DIR / "pipeline.log"

# ==============================================================================
# 3. DATA SCHEMA & CLEANING CONSTANTS
# ==============================================================================
REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

DEFAULT_DESCRIPTION = "Unknown Product"

# Exclusion keywords for merchandise product analysis
NON_MERCHANDISE_DESCRIPTIONS = ["POSTAGE", "DOTCOM POSTAGE", "POST", "MANUAL", "DISCOUNT", "BANK CHARGES", "AMAZON FEE"]

# ==============================================================================
# 4. REFERENCE BASELINE VALUES (Online Retail 2010-2011 Dataset)
# ==============================================================================
BASELINE_METRICS = {
    "total_revenue": 10642110.80,
    "total_orders": 19960,
    "identified_customers": 4338,
    "average_order_value": 533.17,
    "unique_products": 3922,
    "valid_sales_rows": 524878,
}
