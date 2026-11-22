"""
Unit tests for python/data_validation.py.
"""

import pytest
import pandas as pd
from python.data_cleaning import clean_retail_data
from python.data_validation import validate_cleaned_data, generate_quality_report, DataValidationError


def test_validation_passes_on_valid_data(synthetic_raw_data, tmp_path):
    """Verify that a properly cleaned dataset passes all critical data quality checks."""
    sales, _, _ = clean_retail_data(synthetic_raw_data)
    is_valid, quality_df, errors = validate_cleaned_data(sales)
    assert is_valid is True
    assert len(errors) == 0

    report_file = tmp_path / "test_quality_report.csv"
    valid, report = generate_quality_report(sales, report_path=report_file)
    assert valid is True
    assert report_file.exists()


def test_validation_fails_on_negative_quantity(synthetic_raw_data):
    """Verify that validation flags non-positive quantities as critical errors."""
    sales, _, _ = clean_retail_data(synthetic_raw_data)
    corrupted_sales = sales.copy()
    corrupted_sales.loc[0, "Quantity"] = -5

    is_valid, quality_df, errors = validate_cleaned_data(corrupted_sales)
    assert is_valid is False
    assert any("Quantity <= 0" in err for err in errors)


def test_validation_fails_on_revenue_mismatch(synthetic_raw_data):
    """Verify that validation catches math inaccuracies between Revenue and Quantity * Price."""
    sales, _, _ = clean_retail_data(synthetic_raw_data)
    corrupted_sales = sales.copy()
    corrupted_sales.loc[0, "Revenue"] = 99999.0  # Injected calculation error

    is_valid, quality_df, errors = validate_cleaned_data(corrupted_sales)
    assert is_valid is False
    assert any("revenue calculation mismatches" in err for err in errors)


def test_validation_fails_on_cancelled_invoices(synthetic_raw_data):
    """Verify that validation flags cancelled invoices starting with 'C'."""
    sales, _, _ = clean_retail_data(synthetic_raw_data)
    corrupted_sales = sales.copy()
    corrupted_sales.loc[0, "InvoiceNo"] = "C99999"

    is_valid, quality_df, errors = validate_cleaned_data(corrupted_sales)
    assert is_valid is False
    assert any("cancelled invoices" in err for err in errors)
