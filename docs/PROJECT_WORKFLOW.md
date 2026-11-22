# Automated Business Performance Dashboard - Project Workflow & Architecture

This document details the architectural design, end-to-end data pipeline stages, mathematical calculations, and quality validation gates implemented in the Automated Business Performance Dashboard.

---

## 1. High-Level Architecture

The system transitions raw transactional records through automated cleaning, validation, database loading, and business analytics stages into refreshed reporting outputs:

```
[ Raw Excel / CSV ] (data/raw/)
         │
         ▼
[ Ingestion & Deduplication ] (python/data_cleaning.py)
         │
         ├── Non-Sales Transactions (data/processed/non_sales_transactions.csv)
         │   (Cancellations, Quantity <= 0, UnitPrice <= 0)
         │
         ▼
[ Valid Sales Transformation ] (524,878 records)
         │
         ▼
[ Automated Data Quality Audit ] (python/data_validation.py)
         │
         ├── Generates: reports/data_quality_report.csv
         │   (Checks math accuracy, positive constraints, null dates)
         │
         ▼
[ Idempotent SQLite Database Load ] (python/database_manager.py)
         │
         ├── Transaction rollback on failure
         ├── Indexed by: InvoiceNo, StockCode, CustomerID, InvoiceDate, Country
         ├── File Hash Change Detection & Ingestion Audit (pipeline_runs)
         │
         ▼
[ Multi-Dimensional Business Analytics ] (python/business_analysis.py)
         │
         ├── reports/business_summary.csv
         ├── reports/monthly_sales_summary.csv
         ├── reports/country_sales_summary.csv
         ├── reports/product_sales_summary.csv
         ├── reports/customer_sales_summary.csv
         └── reports/pipeline_run_summary.txt
         │
         ▼
[ Power BI Interactive Dashboard ] (powerbi/Automated_Business_Dashboard.pbix)
```

---

## 2. Pipeline Stages Detailed

### Stage 1: Data Ingestion & Change Detection
- **Folder**: `data/raw/`
- **Supported Formats**: Excel (`.xlsx`, `.xls`) and CSV (`.csv`).
- **File Hashing**: Calculates a SHA-256 fingerprint for every input file.
- **Idempotency**: If a file has already been successfully ingested and has not changed, the pipeline avoids redundant processing unless invoked with `--force`.

### Stage 2: Data Cleaning & Non-Sales Separation
- **Deduplication**: Removes exact row duplicates (5,268 rows removed in historical benchmark).
- **Cancelled Invoices**: Identifies invoices starting with `'C'` (e.g., `C536379`) and routes them to `data/processed/non_sales_transactions.csv`.
- **Negative/Zero Values**: Filters out records where `Quantity <= 0` or `UnitPrice <= 0`.
- **Missing Descriptions**: Replaces null product descriptions with `"Unknown Product"` while preserving all order financial records.
- **Date Standardization**: Validates and converts `InvoiceDate` to ISO 8601 datetimes. Drops unparseable timestamp rows.
- **Customer ID Integrity**: Retains sales rows with unassigned `CustomerID` as nullable integers (`Int64`) so total business sales and order totals remain 100% accurate.
- **Revenue Calculation**:
  $$\text{Revenue} = \text{Quantity} \times \text{UnitPrice}$$

### Stage 3: Automated Data Quality Audits
Before database insertion, `python/data_validation.py` executes 10 automated quality assertions:
1. **Required Schema**: All 8 mandatory source columns present.
2. **Positive Quantities**: 0 records with $\text{Quantity} \le 0$.
3. **Positive Unit Prices**: 0 records with $\text{UnitPrice} \le 0$.
4. **No Cancelled Invoices**: 0 records beginning with `'C'` in sales dataset.
5. **Valid Dates**: 0 unparseable or null timestamps.
6. **Mathematical Accuracy**: Validates that $\text{Revenue} = \text{Quantity} \times \text{UnitPrice}$ within a £0.01 tolerance across 100% of rows.
7. **Description Completeness**: 0 null product descriptions.
8. **Missing Customer ID Tracking**: Quantifies and documents missing customer percentages.
9. **Zero Exact Duplicates**: 0 duplicate rows remaining.
10. **Row Count Threshold**: Verifies non-empty output.

### Stage 4: Database Ingestion & Transaction Safety
- **Engine**: SQLite 3 (`database/retail_business.db`).
- **Table**: `sales` with strict column constraints.
- **Indexes**: Multi-column coverage on `InvoiceNo`, `StockCode`, `CustomerID`, `InvoiceDate`, `Country`, and `SourceFile`.
- **Rollback Guarantee**: Ingestion occurs inside explicit `BEGIN TRANSACTION` blocks. If any error occurs, all changes are rolled back automatically, preventing database corruption.

### Stage 5: Business Performance Analysis
Generates 5 dedicated summaries in `reports/`:
- **Executive KPIs**: Total Revenue, Total Orders, Average Order Value (AOV), Identified Customers, Unique Products, Total Quantity Sold.
- **Monthly Revenue**: Monthly trend breakdown with monthly order counts and AOV.
- **Country Performance**: Revenue ranking by country with market share percentage.
- **Product Rankings**: Top merchandise products excluding postage, manual entries, and bank fees.
- **Customer Segmentation**: Top spending customers, order frequencies, and average order spend.

---

## 3. Reference Baseline Benchmarks (Online Retail 2010–2011)

| Metric | Reference Value | Business Interpretation |
|---|---|---|
| **Total Revenue** | **£10,642,110.80** | Gross sales from positive merchandise transactions |
| **Total Orders** | **19,960** | Unique valid invoice numbers |
| **Identified Customers** | **4,338** | Unique customer accounts with non-null IDs |
| **Average Order Value (AOV)** | **£533.17** | Total Revenue / Total Orders |
| **Unique Products** | **3,922** | Unique merchandise StockCodes sold |
| **Cleaned Sales Rows** | **524,878** | Final verified sales transaction lines |

*Note: December 2011 represents a partial month terminating on December 9, 2011.*
