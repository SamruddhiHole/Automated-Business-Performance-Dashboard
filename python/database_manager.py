"""
Database Manager Module.

Manages SQLite database connections, schema migrations, transactional data loading,
indexing, idempotency (duplicate file prevention), and analytical query execution.
"""

import sys
import hashlib
import sqlite3
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import pandas as pd

# Add parent directory to path so config can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


class DatabaseManager:
    """Manages SQLite database operations with transaction safety and idempotency."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or config.DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Initializes database schema and indexes from schema.sql and handles column migrations."""
        schema_file = config.SQL_DIR / "schema.sql"
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file missing: {schema_file}")

        with schema_file.open("r", encoding="utf-8") as f:
            schema_script = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if sales table exists and check its columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sales'")
            sales_exists = cursor.fetchone() is not None

            if sales_exists:
                cursor.execute("PRAGMA table_info(sales)")
                existing_cols = [row["name"] for row in cursor.fetchall()]
                if "SourceFile" not in existing_cols:
                    cursor.execute("ALTER TABLE sales ADD COLUMN SourceFile TEXT DEFAULT 'Online Retail.xlsx'")

            # Execute schema script
            conn.executescript(schema_script)
            conn.commit()

    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Computes SHA-256 hash of a file for change detection."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_file_already_processed(self, source_file: str, file_hash: str) -> bool:
        """Checks if a file with the given hash has already been successfully processed."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT run_id FROM pipeline_runs
                WHERE file_hash = ? AND status = 'SUCCESS'
                ORDER BY run_id DESC LIMIT 1
                """,
                (file_hash,),
            )
            return cursor.fetchone() is not None

    def load_sales_data(
        self,
        df: pd.DataFrame,
        source_name: str = "Online Retail.xlsx",
        file_hash: str = "manual_load",
        force_replace: bool = True,
    ) -> Tuple[int, Dict[str, Any]]:
        """Atomically loads cleaned sales records into the sales table.

        Args:
            df: Cleaned sales DataFrame (9 canonical columns).
            source_name: Filename of source data.
            file_hash: SHA-256 hash of the input file.
            force_replace: If True, replaces previous records for this source file.

        Returns:
            Tuple of (rows_inserted, verification_metrics).
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Begin explicit transaction
            cursor.execute("BEGIN TRANSACTION")

            if force_replace:
                cursor.execute("DELETE FROM sales WHERE SourceFile = ?", (source_name,))

            # Prepare records for batch insertion
            insert_sql = """
                INSERT INTO sales (
                    InvoiceNo, StockCode, Description, Quantity,
                    InvoiceDate, UnitPrice, CustomerID, Country, Revenue, SourceFile
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            records = []
            for row in df.itertuples(index=False):
                # Handle nullable CustomerID
                cust_id = int(row.CustomerID) if pd.notna(row.CustomerID) else None
                records.append((
                    str(row.InvoiceNo),
                    str(row.StockCode),
                    str(row.Description),
                    int(row.Quantity),
                    str(row.InvoiceDate),
                    float(row.UnitPrice),
                    cust_id,
                    str(row.Country),
                    float(row.Revenue),
                    source_name,
                ))

            cursor.executemany(insert_sql, records)
            rows_inserted = len(records)

            # Record in pipeline_runs
            total_rev = round(float(df["Revenue"].sum()), 2)
            cursor.execute(
                """
                INSERT INTO pipeline_runs (
                    run_timestamp, source_file, file_hash, total_raw_rows,
                    valid_sales_rows, excluded_rows, total_revenue, status, details
                ) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, 'SUCCESS', ?)
                """,
                (
                    source_name,
                    file_hash,
                    rows_inserted,
                    rows_inserted,
                    0,
                    total_rev,
                    f"Successfully inserted {rows_inserted:,} records",
                ),
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Database insertion failed and was rolled back: {e}") from e
        finally:
            conn.close()

        # Run verification query
        verification = self.get_database_summary()
        return rows_inserted, verification

    def get_database_summary(self) -> Dict[str, Any]:
        """Queries database for verification totals."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*) AS Total_Records,
                    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
                    COUNT(DISTINCT StockCode) AS Unique_Products,
                    COUNT(DISTINCT CustomerID) AS Identified_Customers,
                    ROUND(SUM(Revenue), 2) AS Total_Revenue,
                    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS Average_Order_Value,
                    SUM(Quantity) AS Total_Quantity_Sold
                FROM sales
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "total_records": row["Total_Records"],
                    "total_orders": row["Total_Orders"],
                    "unique_products": row["Unique_Products"],
                    "identified_customers": row["Identified_Customers"],
                    "total_revenue": row["Total_Revenue"] or 0.0,
                    "average_order_value": row["Average_Order_Value"] or 0.0,
                    "total_quantity_sold": row["Total_Quantity_Sold"] or 0,
                }
            return {}


if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized successfully at:", db.db_path)
    summary = db.get_database_summary()
    print("Current Database Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
