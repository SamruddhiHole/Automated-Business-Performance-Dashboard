"""
Data Overview Module.

Provides comprehensive inspection and structural summary of raw and processed
retail datasets, including row counts, column names, missing values, duplicates,
and summary statistics.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


def inspect_dataset(file_path: Path) -> pd.DataFrame:
    """Inspects a dataset file (Excel or CSV) and prints an overview.

    Args:
        file_path: Path to the Excel or CSV file.

    Returns:
        Loaded pandas DataFrame.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"[-] ERROR: File not found: {path}")
        return pd.DataFrame()

    print("=" * 60)
    print(f"DATASET OVERVIEW: {path.name}")
    print("=" * 60)

    # Load based on extension
    if path.suffix.lower() in [".xlsx", ".xls"]:
        print(f"Loading Excel file: {path} ...")
        df = pd.read_excel(path)
    else:
        print(f"Loading CSV file: {path} ...")
        df = pd.read_csv(path, low_memory=False)

    print("\n1. Dataset Dimensions:")
    print(f"   - Rows: {df.shape[0]:,}")
    print(f"   - Columns: {df.shape[1]}")

    print("\n2. Columns & Data Types:")
    for col, dtype in df.dtypes.items():
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        print(f"   - {col:<15} ({str(dtype):<10}) | Missing: {missing_count:>6,} ({missing_pct:>5.1f}%)")

    duplicate_rows = df.duplicated().sum()
    print(f"\n3. Duplicate Rows: {duplicate_rows:,} ({(duplicate_rows/len(df))*100:.2f}%)")

    print("\n4. First 3 Sample Records:")
    print(df.head(3).to_string())

    print("\n5. Summary Statistics:")
    print(df.describe(include="all").to_string())
    print("=" * 60)

    return df


if __name__ == "__main__":
    # Default inspection: inspect raw file if present, else cleaned sales
    raw_candidates = list(config.RAW_DATA_DIR.glob("*.xlsx")) + list(config.RAW_DATA_DIR.glob("*.csv"))
    if raw_candidates:
        inspect_dataset(raw_candidates[0])
    elif config.CLEANED_SALES_CSV.exists():
        inspect_dataset(config.CLEANED_SALES_CSV)
    else:
        print("[-] No dataset found in data/raw or data/processed.")
