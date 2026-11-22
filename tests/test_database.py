"""
Unit tests for python/database_manager.py.
"""

import pytest
import sqlite3
import pandas as pd
from python.data_cleaning import clean_retail_data
from python.database_manager import DatabaseManager


def test_database_initialization(tmp_path):
    """Verify database schema creation and table initialization."""
    db_file = tmp_path / "test_retail.db"
    db_manager = DatabaseManager(db_path=db_file)
    assert db_file.exists()

    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]
        assert "sales" in tables
        assert "pipeline_runs" in tables


def test_sales_data_loading_and_summary(tmp_path, synthetic_raw_data):
    """Verify transactional loading of sales records and accurate summary retrieval."""
    db_file = tmp_path / "test_retail.db"
    db_manager = DatabaseManager(db_path=db_file)
    sales, _, _ = clean_retail_data(synthetic_raw_data)

    inserted, summary = db_manager.load_sales_data(
        sales,
        source_name="test_data.xlsx",
        file_hash="dummy_hash_123",
        force_replace=True,
    )

    assert inserted == len(sales)
    assert summary["total_records"] == len(sales)
    assert summary["total_revenue"] == round(sales["Revenue"].sum(), 2)


def test_duplicate_file_detection(tmp_path, synthetic_raw_data):
    """Verify that processed files are logged in pipeline_runs to prevent duplicate imports."""
    db_file = tmp_path / "test_retail.db"
    db_manager = DatabaseManager(db_path=db_file)
    sales, _, _ = clean_retail_data(synthetic_raw_data)

    test_hash = "unique_file_hash_999"
    assert not db_manager.is_file_already_processed("test.xlsx", test_hash)

    db_manager.load_sales_data(sales, source_name="test.xlsx", file_hash=test_hash)
    assert db_manager.is_file_already_processed("test.xlsx", test_hash)


def test_transaction_rollback_on_failure(tmp_path, synthetic_raw_data):
    """Verify that a database error during loading triggers a rollback, leaving table clean."""
    db_file = tmp_path / "test_retail.db"
    db_manager = DatabaseManager(db_path=db_file)
    sales, _, _ = clean_retail_data(synthetic_raw_data)

    # Intentionally corrupt a row to trigger SQLite CHECK constraint (Quantity > 0)
    bad_df = sales.copy()
    bad_df.loc[0, "Quantity"] = -99

    with pytest.raises(RuntimeError):
        db_manager.load_sales_data(bad_df, source_name="corrupt.xlsx", file_hash="bad_hash")

    # Verify that nothing was committed to sales table
    summary = db_manager.get_database_summary()
    assert summary["total_records"] == 0
