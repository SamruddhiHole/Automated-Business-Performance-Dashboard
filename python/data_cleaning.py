"""
Data Cleaning Module.

Implements robust, reusable data cleaning functions for the Online Retail dataset.
Maintains exact compliance with the established data cleaning rules:
1. Remove exact duplicate records.
2. Flag and separate non-sales transactions:
   - Cancelled invoices (InvoiceNo starts with 'C')
   - Non-positive quantities (Quantity <= 0)
   - Non-positive unit prices (UnitPrice <= 0)
3. Fill missing descriptions with 'Unknown Product'.
4. Convert InvoiceDate to valid datetime (drop invalid dates).
5. Retain records with missing CustomerID (converted to nullable integer Int64).
6. Calculate Revenue = Quantity * UnitPrice.
7. Separate valid sales and non-sales transactions into distinct outputs.
"""

import sys
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def load_raw_data(file_path: Path) -> pd.DataFrame:
    """Loads raw transaction data from an Excel or CSV file.

    Args:
        file_path: Path to the raw data file.

    Returns:
        DataFrame containing the raw transactions.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If required columns are missing.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")

    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path, dtype={"InvoiceNo": str}, low_memory=False)

    # Check for required columns
    missing_cols = [col for col in config.REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in {path.name}: {missing_cols}")

    return df


def clean_retail_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Cleans the raw retail DataFrame according to business rules.

    Args:
        df: Raw DataFrame containing Online Retail transactions.

    Returns:
        Tuple of:
          - valid_sales (pd.DataFrame): 9-column cleaned sales dataset.
          - non_sales (pd.DataFrame): Excluded transactions (cancelled, returns, adjustments).
          - summary (dict): Execution and quality metrics.
    """
    original_rows = len(df)

    # 1. Deduplication
    df_dedup = df.drop_duplicates().copy()
    duplicates_removed = original_rows - len(df_dedup)

    # 2. Identify cancelled invoices (InvoiceNo starting with 'C')
    invoice_str = df_dedup["InvoiceNo"].astype(str).str.strip()
    cancelled_mask = invoice_str.str.startswith("C", na=False)

    # 3. Separate non-sales transactions (cancellations, quantity <= 0, unit price <= 0)
    quantity_numeric = pd.to_numeric(df_dedup["Quantity"], errors="coerce").fillna(0)
    price_numeric = pd.to_numeric(df_dedup["UnitPrice"], errors="coerce").fillna(0)

    non_sales_mask = (
        cancelled_mask
        | (quantity_numeric <= 0)
        | (price_numeric <= 0)
    )

    non_sales = df_dedup[non_sales_mask].copy()
    valid_sales = df_dedup[~non_sales_mask].copy()

    # 4. Fill missing product descriptions
    missing_descriptions = valid_sales["Description"].isna().sum()
    valid_sales["Description"] = valid_sales["Description"].fillna(config.DEFAULT_DESCRIPTION)

    # 5. Convert and validate InvoiceDate
    valid_sales["InvoiceDate"] = pd.to_datetime(valid_sales["InvoiceDate"], errors="coerce")
    invalid_dates_dropped = valid_sales["InvoiceDate"].isna().sum()
    valid_sales = valid_sales.dropna(subset=["InvoiceDate"]).copy()

    # 6. Calculate Gross Sales Revenue
    valid_sales["Quantity"] = pd.to_numeric(valid_sales["Quantity"])
    valid_sales["UnitPrice"] = pd.to_numeric(valid_sales["UnitPrice"])
    valid_sales["Revenue"] = valid_sales["Quantity"] * valid_sales["UnitPrice"]

    # 7. Convert CustomerID to nullable integer (retaining missing IDs for total sales)
    valid_sales["CustomerID"] = pd.to_numeric(valid_sales["CustomerID"], errors="coerce").astype("Int64")

    # 8. Standardize column order (9 canonical columns)
    canonical_columns = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
        "Revenue",
    ]
    valid_sales = valid_sales[canonical_columns].copy()

    # Summary metrics
    missing_cust_id_count = int(valid_sales["CustomerID"].isna().sum())
    total_rev = float(round(valid_sales["Revenue"].sum(), 2))

    summary = {
        "original_rows": original_rows,
        "duplicates_removed": duplicates_removed,
        "records_after_dedup": len(df_dedup),
        "non_sales_records": len(non_sales),
        "valid_sales_records": len(valid_sales),
        "missing_descriptions_filled": int(missing_descriptions),
        "invalid_dates_dropped": int(invalid_dates_dropped),
        "missing_customer_ids": missing_cust_id_count,
        "total_revenue": total_rev,
        "date_min": str(valid_sales["InvoiceDate"].min()) if len(valid_sales) > 0 else None,
        "date_max": str(valid_sales["InvoiceDate"].max()) if len(valid_sales) > 0 else None,
    }

    return valid_sales, non_sales, summary


def process_and_save(input_path: Path, output_sales_path: Path = None, output_non_sales_path: Path = None) -> Dict[str, Any]:
    """Loads raw data, performs cleaning, and persists cleaned outputs.

    Args:
        input_path: Path to the raw dataset.
        output_sales_path: Destination path for cleaned sales CSV (optional).
        output_non_sales_path: Destination path for non-sales CSV (optional).

    Returns:
        Cleaning summary dictionary.
    """
    sales_path = output_sales_path or config.CLEANED_SALES_CSV
    non_sales_path = output_non_sales_path or config.NON_SALES_CSV

    sales_path.parent.mkdir(parents=True, exist_ok=True)
    non_sales_path.parent.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data(input_path)
    sales_df, non_sales_df, summary = clean_retail_data(raw_df)

    sales_df.to_csv(sales_path, index=False)
    non_sales_df.to_csv(non_sales_path, index=False)

    return summary


if __name__ == "__main__":
    raw_files = list(config.RAW_DATA_DIR.glob("*.xlsx")) + list(config.RAW_DATA_DIR.glob("*.csv"))
    if not raw_files:
        # Fallback check
        legacy_raw = config.DATA_DIR / "online+retail" / "Online Retail.xlsx"
        if legacy_raw.exists():
            raw_files = [legacy_raw]

    if raw_files:
        print(f"Cleaning raw file: {raw_files[0]} ...")
        res = process_and_save(raw_files[0])
        print("Cleaning Summary:")
        for k, v in res.items():
            print(f"  {k}: {v}")
    else:
        print("[-] No raw dataset found to clean.")
