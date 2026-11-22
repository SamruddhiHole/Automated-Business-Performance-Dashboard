"""
Data Validation Module.

Performs automated data quality audits on cleaned sales datasets before database
loading and report generation. Produces a detailed Data Quality Report CSV and
enforces schema integrity, mathematical accuracy, and business validation constraints.
"""

import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


class DataValidationError(Exception):
    """Raised when critical data validation rules fail."""
    pass


def validate_cleaned_data(df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, List[str]]:
    """Runs a comprehensive suite of data quality checks on the cleaned sales DataFrame.

    Args:
        df: Cleaned sales DataFrame.

    Returns:
        Tuple containing:
          - is_valid (bool): True if all critical checks passed, False otherwise.
          - quality_report_df (pd.DataFrame): Tabular data quality report.
          - errors (list[str]): List of critical validation failure messages.
    """
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []

    # 1. Check Required Columns
    missing_cols = [col for col in config.REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        err = f"Missing required columns: {missing_cols}"
        errors.append(err)
        checks.append({"Check_Name": "Required Columns", "Status": "FAILED", "Value": len(missing_cols), "Details": err})
    else:
        checks.append({"Check_Name": "Required Columns", "Status": "PASSED", "Value": len(df.columns), "Details": "All required columns present"})

    # 2. Check Row Count
    total_rows = len(df)
    if total_rows == 0:
        err = "Cleaned dataset contains 0 rows."
        errors.append(err)
        checks.append({"Check_Name": "Row Count", "Status": "FAILED", "Value": 0, "Details": err})
    else:
        checks.append({"Check_Name": "Row Count", "Status": "PASSED", "Value": total_rows, "Details": f"{total_rows:,} records available"})

    # 3. Check for Non-Positive Quantities
    non_pos_qty = (df["Quantity"] <= 0).sum()
    if non_pos_qty > 0:
        err = f"Found {non_pos_qty:,} records with Quantity <= 0"
        errors.append(err)
        checks.append({"Check_Name": "Positive Quantities", "Status": "FAILED", "Value": int(non_pos_qty), "Details": err})
    else:
        checks.append({"Check_Name": "Positive Quantities", "Status": "PASSED", "Value": 0, "Details": "All quantities are strictly positive (> 0)"})

    # 4. Check for Non-Positive Unit Prices
    non_pos_price = (df["UnitPrice"] <= 0).sum()
    if non_pos_price > 0:
        err = f"Found {non_pos_price:,} records with UnitPrice <= 0"
        errors.append(err)
        checks.append({"Check_Name": "Positive Unit Prices", "Status": "FAILED", "Value": int(non_pos_price), "Details": err})
    else:
        checks.append({"Check_Name": "Positive Unit Prices", "Status": "PASSED", "Value": 0, "Details": "All unit prices are strictly positive (> 0)"})

    # 5. Check for Cancelled Invoices
    cancelled_count = df["InvoiceNo"].astype(str).str.startswith("C").sum()
    if cancelled_count > 0:
        err = f"Found {cancelled_count:,} cancelled invoices in cleaned sales"
        errors.append(err)
        checks.append({"Check_Name": "No Cancelled Invoices", "Status": "FAILED", "Value": int(cancelled_count), "Details": err})
    else:
        checks.append({"Check_Name": "No Cancelled Invoices", "Status": "PASSED", "Value": 0, "Details": "Zero cancelled invoices present in sales"})

    # 6. Check for Invalid or Missing Dates
    dates = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    null_dates = dates.isna().sum()
    if null_dates > 0:
        err = f"Found {null_dates:,} invalid or missing dates"
        errors.append(err)
        checks.append({"Check_Name": "Valid Dates", "Status": "FAILED", "Value": int(null_dates), "Details": err})
    else:
        checks.append({"Check_Name": "Valid Dates", "Status": "PASSED", "Value": 0, "Details": f"Date span: {dates.min()} to {dates.max()}"})

    # 7. Check Mathematical Accuracy of Revenue
    expected_rev = (df["Quantity"] * df["UnitPrice"]).round(2)
    actual_rev = df["Revenue"].round(2)
    rev_discrepancies = (~np.isclose(expected_rev, actual_rev, atol=0.01)).sum()
    if rev_discrepancies > 0:
        err = f"Found {rev_discrepancies:,} revenue calculation mismatches"
        errors.append(err)
        checks.append({"Check_Name": "Revenue Accuracy", "Status": "FAILED", "Value": int(rev_discrepancies), "Details": err})
    else:
        total_rev = round(df["Revenue"].sum(), 2)
        checks.append({"Check_Name": "Revenue Accuracy", "Status": "PASSED", "Value": total_rev, "Details": f"All revenue values exact. Total: £{total_rev:,.2f}"})

    # 8. Check Missing Product Descriptions
    null_desc = df["Description"].isna().sum()
    if null_desc > 0:
        err = f"Found {null_desc:,} null descriptions"
        errors.append(err)
        checks.append({"Check_Name": "No Missing Descriptions", "Status": "FAILED", "Value": int(null_desc), "Details": err})
    else:
        unknown_desc = (df["Description"] == config.DEFAULT_DESCRIPTION).sum()
        checks.append({"Check_Name": "No Missing Descriptions", "Status": "PASSED", "Value": int(unknown_desc), "Details": f"Zero nulls ({unknown_desc:,} filled with '{config.DEFAULT_DESCRIPTION}')"})

    # 9. Informational: Missing CustomerID Tracking
    null_cust = df["CustomerID"].isna().sum()
    null_cust_pct = (null_cust / total_rows) * 100 if total_rows > 0 else 0
    checks.append({
        "Check_Name": "Missing Customer IDs (Retained)",
        "Status": "INFO",
        "Value": int(null_cust),
        "Details": f"{null_cust:,} records ({null_cust_pct:.1f}%) have unassigned CustomerID; retained per business rules"
    })

    # 10. Check for Exact Duplicate Rows
    exact_duplicates = df.duplicated().sum()
    if exact_duplicates > 0:
        err = f"Found {exact_duplicates:,} exact duplicate rows"
        errors.append(err)
        checks.append({"Check_Name": "Zero Exact Duplicates", "Status": "FAILED", "Value": int(exact_duplicates), "Details": err})
    else:
        checks.append({"Check_Name": "Zero Exact Duplicates", "Status": "PASSED", "Value": 0, "Details": "No duplicate rows detected"})

    quality_df = pd.DataFrame(checks)
    is_valid = len(errors) == 0

    return is_valid, quality_df, errors


def generate_quality_report(df: pd.DataFrame, report_path: Path = None) -> Tuple[bool, pd.DataFrame]:
    """Validates the dataset and saves the Data Quality Report CSV.

    Args:
        df: Cleaned sales DataFrame.
        report_path: Destination path for CSV report (defaults to config.DATA_QUALITY_REPORT).

    Returns:
        Tuple of (is_valid, quality_df).

    Raises:
        DataValidationError: If validation fails critically.
    """
    out_path = report_path or config.DATA_QUALITY_REPORT
    out_path.parent.mkdir(parents=True, exist_ok=True)

    is_valid, quality_df, errors = validate_cleaned_data(df)
    quality_df.to_csv(out_path, index=False)

    if not is_valid:
        error_msg = "; ".join(errors)
        raise DataValidationError(f"Data quality validation failed: {error_msg}")

    return is_valid, quality_df


if __name__ == "__main__":
    if config.CLEANED_SALES_CSV.exists():
        print(f"Validating: {config.CLEANED_SALES_CSV} ...")
        df_sales = pd.read_csv(config.CLEANED_SALES_CSV, dtype={"InvoiceNo": str}, low_memory=False)
        valid, report = generate_quality_report(df_sales)
        print("\nData Quality Report:")
        print(report.to_string(index=False))
        print(f"\nReport saved to: {config.DATA_QUALITY_REPORT}")
    else:
        print("[-] Cleaned sales CSV not found to validate.")
