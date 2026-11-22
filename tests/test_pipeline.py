"""
Integration tests for the automated pipeline and summary report generation.
"""

import pytest
import pandas as pd
from python.automated_pipeline import run_pipeline
from python.business_analysis import run_all_business_analyses
from python.data_cleaning import clean_retail_data
import config


def test_business_analysis_summaries(synthetic_raw_data, tmp_path):
    """Verify that all required business summary CSVs are generated with expected columns."""
    sales, _, _ = clean_retail_data(synthetic_raw_data)
    summaries = run_all_business_analyses(sales)

    assert "kpi" in summaries
    assert "monthly" in summaries
    assert "country" in summaries
    assert "product" in summaries
    assert "customer" in summaries

    # Check files created on disk
    assert config.BUSINESS_SUMMARY.exists()
    assert config.MONTHLY_SALES_SUMMARY.exists()
    assert config.COUNTRY_SALES_SUMMARY.exists()
    assert config.PRODUCT_SALES_SUMMARY.exists()
    assert config.CUSTOMER_SALES_SUMMARY.exists()


def test_pipeline_dry_run(synthetic_raw_data, tmp_path):
    """Verify that dry-run mode validates data without modifying the database."""
    test_csv = tmp_path / "synthetic_test.csv"
    synthetic_raw_data.to_csv(test_csv, index=False)

    test_db = tmp_path / "test_dry_run.db"
    success = run_pipeline(test_csv, dry_run=True, force=True, db_path=test_db)
    assert success is True


def test_end_to_end_pipeline_execution(synthetic_raw_data, tmp_path):
    """Verify complete end-to-end pipeline execution from raw CSV to reports and summaries."""
    test_csv = tmp_path / "synthetic_sales.csv"
    synthetic_raw_data.to_csv(test_csv, index=False)

    test_db = tmp_path / "test_pipe_isolated.db"
    success = run_pipeline(test_csv, dry_run=False, force=True, db_path=test_db)
    assert success is True
    assert config.PIPELINE_RUN_SUMMARY.exists()
    assert config.DATA_QUALITY_REPORT.exists()
