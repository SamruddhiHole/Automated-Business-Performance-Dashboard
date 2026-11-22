"""
Unit tests for python/data_cleaning.py.
"""

import pytest
import pandas as pd
from python.data_cleaning import clean_retail_data
import config


def test_duplicate_removal(synthetic_raw_data):
    """Verify that exact duplicate records are removed."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert summary["duplicates_removed"] == 1
    assert summary["records_after_dedup"] == 8


def test_cancelled_invoice_exclusion(synthetic_raw_data):
    """Verify that invoices beginning with 'C' are excluded from valid sales."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert not sales["InvoiceNo"].str.startswith("C").any()
    assert (non_sales["InvoiceNo"] == "C10003").any()


def test_non_positive_quantity_exclusion(synthetic_raw_data):
    """Verify that transactions with Quantity <= 0 are excluded from valid sales."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert (sales["Quantity"] > 0).all()
    assert (non_sales["InvoiceNo"] == "10004").any()


def test_non_positive_unitprice_exclusion(synthetic_raw_data):
    """Verify that transactions with UnitPrice <= 0 are excluded from valid sales."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert (sales["UnitPrice"] > 0).all()
    assert (non_sales["InvoiceNo"] == "10005").any()


def test_missing_description_filling(synthetic_raw_data):
    """Verify that missing product descriptions are replaced with 'Unknown Product'."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert sales["Description"].isna().sum() == 0
    e505 = sales[sales["StockCode"] == "E505"]
    assert len(e505) == 1
    assert e505.iloc[0]["Description"] == config.DEFAULT_DESCRIPTION


def test_invalid_date_handling(synthetic_raw_data):
    """Verify that rows with unparseable dates are removed."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    assert not (sales["StockCode"] == "F606").any()
    assert summary["invalid_dates_dropped"] == 1


def test_revenue_calculation(synthetic_raw_data):
    """Verify Revenue = Quantity * UnitPrice calculation."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    expected_revenue = sales["Quantity"] * sales["UnitPrice"]
    pd.testing.assert_series_equal(sales["Revenue"], expected_revenue, check_names=False)


def test_missing_customer_id_retention(synthetic_raw_data):
    """Verify that records with missing CustomerID are retained in sales data."""
    sales, non_sales, summary = clean_retail_data(synthetic_raw_data)
    # Record 9 (Silk Scarf) should be present
    g707 = sales[sales["StockCode"] == "G707"]
    assert len(g707) == 1
    assert pd.isna(g707.iloc[0]["CustomerID"])
    assert summary["missing_customer_ids"] == 1
