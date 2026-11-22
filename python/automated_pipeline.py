"""
Automated Data Pipeline Orchestrator.

Master entry point for the Automated Business Performance Dashboard.
Coordinates:
  1. Input File Detection & Ingestion (from data/raw/)
  2. Data Cleaning & Non-Sales Transaction Separation
  3. Automated Data Quality Audits & Reporting
  4. Idempotent & Transaction-Safe SQLite Database Loading
  5. Multi-dimensional Business Analytics & Reporting
  6. Comprehensive Python Logging & Execution Summary Output

Usage:
  python python/automated_pipeline.py
  python python/automated_pipeline.py --input "data/raw/Online Retail.xlsx"
  python python/automated_pipeline.py --all
  python python/automated_pipeline.py --force
  python python/automated_pipeline.py --dry-run
"""

import sys
import argparse
import datetime
import logging
from pathlib import Path
from typing import List, Optional

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from python.data_cleaning import load_raw_data, clean_retail_data
from python.data_validation import generate_quality_report, DataValidationError
from python.database_manager import DatabaseManager
from python.business_analysis import run_all_business_analyses


def configure_logger() -> logging.Logger:
    """Configures project logger with console and rotating file output."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("AutomatedPipeline")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on multiple runs
    if not logger.handlers:
        # File Handler
        fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(fh_format)
        logger.addHandler(fh)

        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch_format = logging.Formatter("[%(levelname)s] %(message)s")
        ch.setFormatter(ch_format)
        logger.addHandler(ch)

    return logger


def find_input_files(explicit_input: Optional[str] = None) -> List[Path]:
    """Identifies eligible raw input files in data/raw/ or explicit path."""
    if explicit_input:
        path = Path(explicit_input)
        if not path.is_absolute():
            path = config.BASE_DIR / path
        if not path.exists():
            raise FileNotFoundError(f"Specified input file does not exist: {path}")
        return [path]

    # Search in data/raw
    valid_exts = [".xlsx", ".xls", ".csv"]
    files = [f for f in config.RAW_DATA_DIR.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]

    # Fallback to data/online+retail if data/raw is empty
    if not files:
        legacy_dir = config.DATA_DIR / "online+retail"
        if legacy_dir.exists():
            files = [f for f in legacy_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]

    return sorted(files)


def run_pipeline(
    input_file: Path,
    dry_run: bool = False,
    force: bool = False,
    db_path: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Executes the end-to-end data pipeline for a single input file.

    Args:
        input_file: Path to the raw data file.
        dry_run: If True, executes cleaning and validation without database commits.
        force: If True, reprocesses file even if already processed.
        db_path: Optional custom database path (used during testing).
        logger: Logger instance.

    Returns:
        True if pipeline succeeded, False otherwise.
    """
    logger = logger or configure_logger()
    start_time = datetime.datetime.now()

    logger.info("=" * 65)
    logger.info(f"STARTING PIPELINE EXECUTION FOR: {input_file.name}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'PRODUCTION'} | Force Reprocess: {force}")
    logger.info("=" * 65)

    db_manager = DatabaseManager(db_path=db_path)

    # Step 1: Check Ingestion History & File Hash
    file_hash = db_manager.calculate_file_hash(input_file)
    logger.info(f"File SHA-256 Hash: {file_hash[:16]}...")

    if not force and db_manager.is_file_already_processed(input_file.name, file_hash):
        logger.info(f"[!] File '{input_file.name}' has already been processed with identical content.")
        logger.info("    To force reprocessing, use the --force flag.")
        return True

    try:
        # Step 2: Ingestion & Raw Validation
        logger.info("\n--- STEP 1 & 2: INGESTION & DATA CLEANING ---")
        raw_df = load_raw_data(input_file)
        raw_rows = len(raw_df)
        logger.info(f"Loaded {raw_rows:,} raw records.")

        sales_df, non_sales_df, summary = clean_retail_data(raw_df)
        logger.info(f"Deduplication: Removed {summary['duplicates_removed']:,} exact duplicates.")
        logger.info(f"Non-Sales Excluded: {summary['non_sales_records']:,} (cancellations, returns, non-positive values).")
        logger.info(f"Valid Sales Retained: {summary['valid_sales_records']:,} records.")
        logger.info(f"Missing Customer IDs: {summary['missing_customer_ids']:,} retained in sales.")
        logger.info(f"Total Gross Revenue: £{summary['total_revenue']:,.2f}")

        # Step 3: Data Quality Validation
        logger.info("\n--- STEP 3: AUTOMATED DATA QUALITY AUDIT ---")
        is_valid, quality_df = generate_quality_report(sales_df)
        logger.info("All critical data quality checks PASSED.")
        logger.info(f"Data Quality Report saved to: {config.DATA_QUALITY_REPORT}")

        if dry_run:
            logger.info("\n[DRY RUN] Skipping database load, persistence, and output generation.")
            logger.info("Validation completed successfully without altering existing data.")
            return True

        # Step 4: Output Persistence (CSV)
        logger.info("\n--- STEP 4: PERSISTING CLEANED DATASETS ---")
        sales_df.to_csv(config.CLEANED_SALES_CSV, index=False)
        non_sales_df.to_csv(config.NON_SALES_CSV, index=False)
        logger.info(f"Saved: {config.CLEANED_SALES_CSV}")
        logger.info(f"Saved: {config.NON_SALES_CSV}")

        # Step 5: Database Loading
        logger.info("\n--- STEP 5: SQLITE DATABASE UPDATE ---")
        inserted, db_summary = db_manager.load_sales_data(
            sales_df,
            source_name=input_file.name,
            file_hash=file_hash,
            force_replace=True,
        )
        logger.info(f"Database Updated: Inserted {inserted:,} sales rows into 'sales' table.")
        logger.info(f"Database Verified - Orders: {db_summary.get('total_orders', 0):,}, "
                    f"Revenue: £{db_summary.get('total_revenue', 0.0):,.2f}")

        # Step 6: Automated Business Analysis & Summary Reports
        logger.info("\n--- STEP 6: BUSINESS ANALYSIS & SUMMARY REPORTS ---")
        summaries = run_all_business_analyses(sales_df)
        logger.info(f"Generated 5 Summary Reports in: {config.REPORTS_DIR}")

        # Step 7: Final Execution Summary File
        end_time = datetime.datetime.now()
        duration_sec = round((end_time - start_time).total_seconds(), 2)

        summary_text = f"""======================================================================
AUTOMATED BUSINESS PERFORMANCE DASHBOARD - PIPELINE EXECUTION SUMMARY
======================================================================
Execution Timestamp : {start_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration            : {duration_sec} seconds
Input File          : {input_file.name}
File Path           : {input_file}
File SHA-256        : {file_hash}
Status              : SUCCESS

RAW DATA METRICS:
-----------------
Total Raw Rows Ingested     : {raw_rows:,}
Duplicate Rows Removed      : {summary['duplicates_removed']:,}
Non-Sales Records Excluded  : {summary['non_sales_records']:,}
Valid Sales Records Saved   : {summary['valid_sales_records']:,}
Missing Customer IDs        : {summary['missing_customer_ids']:,} (Retained in sales)

EXECUTIVE BUSINESS KPIS:
------------------------
Total Revenue               : £{summary['total_revenue']:,.2f}
Total Orders                : {db_summary.get('total_orders', 0):,}
Identified Customers        : {db_summary.get('identified_customers', 0):,}
Unique Products             : {db_summary.get('unique_products', 0):,}
Average Order Value         : £{db_summary.get('average_order_value', 0.0):,.2f}
Total Quantity Sold         : {db_summary.get('total_quantity_sold', 0):,}

DATABASE VERIFICATION:
----------------------
Database File               : {db_manager.db_path}
Table Updated               : sales
Records in Database         : {db_summary.get('total_records', 0):,}

GENERATED OUTPUTS:
------------------
1. Cleaned Sales CSV        : {config.CLEANED_SALES_CSV}
2. Non-Sales CSV            : {config.NON_SALES_CSV}
3. Data Quality Report      : {config.DATA_QUALITY_REPORT}
4. Business Summary         : {config.BUSINESS_SUMMARY}
5. Monthly Sales Summary    : {config.MONTHLY_SALES_SUMMARY}
6. Country Sales Summary    : {config.COUNTRY_SALES_SUMMARY}
7. Product Sales Summary    : {config.PRODUCT_SALES_SUMMARY}
8. Customer Sales Summary   : {config.CUSTOMER_SALES_SUMMARY}
9. Execution Log            : {config.LOG_FILE}
======================================================================
"""
        with open(config.PIPELINE_RUN_SUMMARY, "w", encoding="utf-8") as f:
            f.write(summary_text)

        logger.info(f"\nExecution Summary saved to: {config.PIPELINE_RUN_SUMMARY}")
        print("\n" + summary_text)
        return True

    except Exception as e:
        logger.error(f"PIPELINE EXECUTION FAILED: {e}", exc_info=True)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Automated Retail Business Performance Pipeline"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to specific raw Excel or CSV file"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Process all files found in data/raw/"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force reprocessing even if file was previously processed"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Perform cleaning and validation without modifying database or outputs"
    )

    args = parser.parse_args()
    logger = configure_logger()

    try:
        files = find_input_files(args.input)
    except FileNotFoundError as e:
        logger.error(f"Input Error: {e}")
        sys.exit(1)

    if not files:
        logger.error("No input files found to process in data/raw/. Please add an Excel or CSV file.")
        sys.exit(1)

    targets = files if args.all else [files[0]]
    overall_success = True

    for target_file in targets:
        success = run_pipeline(
            target_file,
            dry_run=args.dry_run,
            force=args.force,
            logger=logger,
        )
        if not success:
            overall_success = False

    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
