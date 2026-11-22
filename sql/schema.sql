-- ==============================================================================
-- Automated Business Performance Dashboard - Database Schema
-- Database: retail_business.db
-- Engine: SQLite 3
-- ==============================================================================

-- 1. Main Sales Table
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    InvoiceNo TEXT NOT NULL,
    StockCode TEXT NOT NULL,
    Description TEXT,
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    InvoiceDate TEXT NOT NULL,
    UnitPrice REAL NOT NULL CHECK (UnitPrice > 0),
    CustomerID INTEGER,
    Country TEXT,
    Revenue REAL NOT NULL,
    SourceFile TEXT DEFAULT 'Online Retail.xlsx'
);

-- 2. Performance Indexes for Fast Analytics & Filtering
CREATE INDEX IF NOT EXISTS idx_sales_invoice ON sales (InvoiceNo);
CREATE INDEX IF NOT EXISTS idx_sales_stock ON sales (StockCode);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales (CustomerID);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales (InvoiceDate);
CREATE INDEX IF NOT EXISTS idx_sales_country ON sales (Country);
CREATE INDEX IF NOT EXISTS idx_sales_source ON sales (SourceFile);

-- 3. Pipeline Run Tracking Table (for Idempotency & Ingestion Auditing)
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_timestamp TEXT NOT NULL,
    source_file TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    total_raw_rows INTEGER NOT NULL,
    valid_sales_rows INTEGER NOT NULL,
    excluded_rows INTEGER NOT NULL,
    total_revenue REAL NOT NULL,
    status TEXT NOT NULL,
    details TEXT
);
