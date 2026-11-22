"""
Pytest fixtures for Automated Business Performance Dashboard.
Provides a fast, synthetic in-memory dataset covering all edge cases.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def synthetic_raw_data() -> pd.DataFrame:
    """Creates a comprehensive synthetic retail dataset covering all cleaning edge cases:

    - 3 valid sales records
    - 1 exact duplicate record
    - 1 cancelled invoice ('C10001')
    - 1 record with Quantity <= 0
    - 1 record with UnitPrice <= 0
    - 1 record with missing Description
    - 1 record with invalid date
    - 1 record with missing CustomerID (valid sale)
    """
    records = [
        # 1. Valid record 1
        {
            "InvoiceNo": "10001",
            "StockCode": "A101",
            "Description": "Vintage Tea Cup",
            "Quantity": 10,
            "InvoiceDate": "2021-01-15 10:30:00",
            "UnitPrice": 2.50,
            "CustomerID": 12345,
            "Country": "United Kingdom",
        },
        # 2. Exact duplicate of record 1
        {
            "InvoiceNo": "10001",
            "StockCode": "A101",
            "Description": "Vintage Tea Cup",
            "Quantity": 10,
            "InvoiceDate": "2021-01-15 10:30:00",
            "UnitPrice": 2.50,
            "CustomerID": 12345,
            "Country": "United Kingdom",
        },
        # 3. Valid record 2
        {
            "InvoiceNo": "10002",
            "StockCode": "B202",
            "Description": "Ceramic Plate Set",
            "Quantity": 4,
            "InvoiceDate": "2021-02-10 14:00:00",
            "UnitPrice": 15.00,
            "CustomerID": 67890,
            "Country": "France",
        },
        # 4. Cancelled invoice
        {
            "InvoiceNo": "C10003",
            "StockCode": "B202",
            "Description": "Ceramic Plate Set",
            "Quantity": -2,
            "InvoiceDate": "2021-02-11 09:15:00",
            "UnitPrice": 15.00,
            "CustomerID": 67890,
            "Country": "France",
        },
        # 5. Invalid quantity (Quantity = 0)
        {
            "InvoiceNo": "10004",
            "StockCode": "C303",
            "Description": "Defective Clock",
            "Quantity": 0,
            "InvoiceDate": "2021-03-01 11:20:00",
            "UnitPrice": 20.00,
            "CustomerID": 11111,
            "Country": "Germany",
        },
        # 6. Invalid unit price (UnitPrice = 0)
        {
            "InvoiceNo": "10005",
            "StockCode": "D404",
            "Description": "Free Gift Item",
            "Quantity": 5,
            "InvoiceDate": "2021-03-05 16:45:00",
            "UnitPrice": 0.00,
            "CustomerID": 22222,
            "Country": "United Kingdom",
        },
        # 7. Missing description (should be filled with 'Unknown Product')
        {
            "InvoiceNo": "10006",
            "StockCode": "E505",
            "Description": None,
            "Quantity": 2,
            "InvoiceDate": "2021-04-12 12:00:00",
            "UnitPrice": 8.00,
            "CustomerID": 33333,
            "Country": "United Kingdom",
        },
        # 8. Invalid date (should be dropped)
        {
            "InvoiceNo": "10007",
            "StockCode": "F606",
            "Description": "Garden Lantern",
            "Quantity": 3,
            "InvoiceDate": "not-a-valid-date",
            "UnitPrice": 12.00,
            "CustomerID": 44444,
            "Country": "Spain",
        },
        # 9. Missing CustomerID (should be retained in sales dataset)
        {
            "InvoiceNo": "10008",
            "StockCode": "G707",
            "Description": "Silk Scarf",
            "Quantity": 1,
            "InvoiceDate": "2021-05-20 17:30:00",
            "UnitPrice": 30.00,
            "CustomerID": None,
            "Country": "United Kingdom",
        },
    ]
    return pd.DataFrame(records)
