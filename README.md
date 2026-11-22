# Automated Business Performance Dashboard

[![CI Pipeline](https://github.com/SamruddhiHole/Automated-Business-Performance-Dashboard/actions/workflows/automated_pipeline.yml/badge.svg)](https://github.com/SamruddhiHole/Automated-Business-Performance-Dashboard/actions/workflows/automated_pipeline.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![SQLite](https://img.shields.io/badge/database-SQLite_3-green.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-yellow.svg)](https://powerbi.microsoft.com/)
[![Tests Passing](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](tests/)

An enterprise-grade, end-to-end automated retail analytics pipeline and interactive business intelligence dashboard built with **Python**, **SQL**, **SQLite**, and **Power BI**. 

Transforms raw transactional records into validated datasets, analytical SQL databases, summary reports, and a four-page executive Power BI dashboard with automated single-command execution and daily scheduling.

---

## 📌 Executive Summary & Key Findings

Analyzing 541,909 raw transactions from the Online Retail dataset (2010–2011) revealed the following validated business benchmarks:

| Executive Metric | Value | Business Context |
|---|---|---|
| **Total Revenue** | **£10,642,110.80** | Gross merchandise sales from 524,878 verified sales transactions |
| **Total Orders** | **19,960** | Unique valid invoice transactions across 38 countries |
| **Identified Customers** | **4,338** | Unique customer accounts with registered IDs |
| **Average Order Value (AOV)** | **£533.17** | Average revenue generated per transaction |
| **Unique Products** | **3,922** | Distinct retail merchandise products sold |
| **Total Units Sold** | **5,572,437** | Aggregate items moved through catalog |

### Core Business Insights:
1. **Geographic Dominance**: The United Kingdom generates over **84% of total revenue**, followed by the Netherlands, EIRE (Ireland), and Germany.
2. **Seasonality & Q4 Surge**: Revenue spikes significantly between September and November, peaking in November at over **£1.4M** due to early holiday preparation. *(Note: December 2011 contains only 9 days of partial data).*
3. **Peak Purchasing Days**: Thursday and Tuesday exhibit the highest transaction volumes and sales totals; weekend order activity is predominantly concentrated on Sundays (with Fridays having shorter ordering hours).
4. **Customer Retention**: High-frequency VIP customers (10+ orders) represent approximately 6% of the customer base but drive more than 35% of total revenue.

---

## 🏗️ Project Architecture

```
[ Raw Dataset: data/raw/ ]
         │
         ▼
[ Automated Ingestion & Cleaning ] ───► Non-Sales Dataset: data/processed/non_sales_transactions.csv
         │                              (Cancellations, Returns, Defective Stock)
         ▼
[ Cleaned Sales Dataset ] (524,878 records)
         │
         ▼
[ Automated Data Quality Audit (10 Rules) ] ───► reports/data_quality_report.csv
         │
         ▼
[ Transaction-Safe SQLite Database ] ───► database/retail_business.db (sales & pipeline_runs)
         │
         ▼
[ Multi-Dimensional Analytics Engine ] ───► reports/business_summary.csv
         │                                 reports/monthly_sales_summary.csv
         │                                 reports/country_sales_summary.csv
         │                                 reports/product_sales_summary.csv
         │                                 reports/customer_sales_summary.csv
         ▼
[ Interactive Power BI Dashboard ] ───► powerbi/Automated_Business_Dashboard.pbix
```

---

## 📁 Repository Structure

```
Automated-Business-Performance-Dashboard/
│
├── config.py                     # Central configuration (paths, schema, benchmarks)
├── requirements.txt              # Pinned Python package dependencies
├── .gitignore                    # Prevents committing large datasets (>50MB) and databases
├── README.md                     # Comprehensive project documentation
│
├── data/
│   ├── raw/                      # Ingestion folder for incoming raw Excel/CSV files
│   └── processed/                # Cleaned sales & non-sales datasets
│       └── eda/                  # Summaries for EDA compatibility
│
├── python/
│   ├── __init__.py
│   ├── automated_pipeline.py     # Master CLI pipeline orchestrator
│   ├── data_cleaning.py          # Modular cleaning & transaction separation
│   ├── data_validation.py        # 10 automated quality checks & report generation
│   ├── database_manager.py       # SQLite connection, migrations, and transactions
│   ├── business_analysis.py      # Multi-dimensional analytics & summary exports
│   └── data_overview.py          # Dataset inspection and statistical profiling
│
├── sql/
│   ├── schema.sql                # Table definitions, constraints, and indexes
│   └── sales_analysis.sql        # Production analytical SQL queries
│
├── database/
│   ├── retail_business.db        # SQLite database (generated locally, excluded from git)
│   └── .gitkeep
│
├── reports/                      # Automated CSV & text outputs from pipeline runs
│   ├── data_quality_report.csv
│   ├── business_summary.csv
│   ├── monthly_sales_summary.csv
│   ├── country_sales_summary.csv
│   ├── product_sales_summary.csv
│   ├── customer_sales_summary.csv
│   └── pipeline_run_summary.txt
│
├── powerbi/
│   └── Automated_Business_Dashboard.pbix # 4-page interactive Power BI dashboard
│
├── screenshots/                  # Dashboard screenshots for presentation
│
├── scripts/
│   ├── run_pipeline_scheduled.bat # Windows batch runner for Task Scheduler
│   └── schedule_task.ps1         # PowerShell task setup utility
│
├── docs/
│   ├── PROJECT_WORKFLOW.md       # Detailed technical architecture & math
│   ├── SETUP_GUIDE.md            # Installation & setup instructions
│   └── POWER_BI_REFRESH_GUIDE.md # Refresh workflows & DAX measure details
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Synthetic test fixtures
│   ├── test_data_cleaning.py     # 8 cleaning unit tests
│   ├── test_data_validation.py   # 4 quality assertion tests
│   ├── test_database.py          # 4 transactional database tests
│   └── test_pipeline.py          # 3 end-to-end integration tests
│
└── .github/
    └── workflows/
        └── automated_pipeline.yml # Automated CI pipeline and quality testing
```

---

## 🧹 Data Cleaning & Validation Rules

Raw transaction records undergo strict business transformation rules:

1. **Deduplication**: Exact row duplicates are eliminated.
2. **Cancellation Handling**: Invoices prefixed with `'C'` are routed to `non_sales_transactions.csv`.
3. **Invalid Quantities & Unit Prices**: Records with Quantity <= 0 or UnitPrice <= 0 are segregated from sales.
4. **Missing Descriptions**: Null product descriptions are filled with `"Unknown Product"` to preserve transaction value.
5. **Datetime Validation**: All timestamps are converted to valid datetimes; unparseable rows are safely dropped.
6. **Customer ID Handling**: Missing Customer IDs are preserved in sales totals (converted to `Int64` nullable integer) but excluded from customer-specific frequency metrics.
7. **Mathematical Accuracy**: Revenue is strictly computed as Quantity * UnitPrice.
8. **Automated Quality Audit**: Before database insertion, 10 checks verify mathematical exactness, non-negativity, and schema integrity, outputting `reports/data_quality_report.csv`.

---

## ⚡ Quick Start & Usage

### 1. Installation
```powershell
# Clone the repository
git clone https://github.com/SamruddhiHole/Automated-Business-Performance-Dashboard.git
cd Automated-Business-Performance-Dashboard

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute Complete Pipeline
Run the entire end-to-end automated pipeline with a single command:

```powershell
python python/automated_pipeline.py
```

### Command-Line Arguments:
```powershell
# Process a specific file
python python/automated_pipeline.py --input "data/raw/Online Retail.xlsx"

# Force reprocessing (skipping hash check)
python python/automated_pipeline.py --force

# Dry run (validates without altering database)
python python/automated_pipeline.py --dry-run

# Process all files in data/raw
python python/automated_pipeline.py --all
```

---

## 📊 Power BI Dashboard Overview

The included report (`powerbi/Automated_Business_Dashboard.pbix`) provides four pages of interactive analysis:

### 1. Business Overview Page
![Business Overview Dashboard](screenshots/Screenshot%202026-11-22%20205831.png)
- **KPI Cards**: Total Revenue (£10.64M), Average Order Value (£533.17), Total Orders (19.96K), Total Customers (4.34K).
- **Monthly Revenue Trend**: Monthly revenue trajectory across 2010–2011.
- **Top 10 Countries**: Market revenue distribution.
- **Top 10 Products**: Revenue leaders.
- **Top 10 Customers**: Top customer spend table.
- **Filters**: Slicers for `Year`, `YearMonth`, and `Country`.

### 2. Sales Analysis Page
![Sales Analysis Dashboard](screenshots/Screenshot%202026-11-22%20205843.png)
- **Transaction Dynamics**: Monthly order volumes, daily revenue curves, and day-of-week sales.
- **Unit Performance**: Monthly quantities sold and comparative sales table.

### 3. Customer Analysis Page
![Customer Analysis Dashboard](screenshots/Screenshot%202026-11-22%20205857.png)
- **Customer Segmentation**: Revenue breakdown by customer purchasing tiers.
- **Order Frequency**: Distribution of one-time vs occasional vs VIP buyers.
- **Average Spend per Customer**: Customer lifetime value metrics.

### 4. Product Analysis Page
![Product Analysis Dashboard](screenshots/Screenshot%202026-11-22%20205908.png)
- **Merchandise Focus**: Rankings excluding non-merchandise fees and postage.
- **Volume vs Value**: Top products by revenue vs top products by units sold.
- **Price Sensitivity**: Average unit prices and revenue trends.

### How to Refresh Power BI:
1. Run `python python/automated_pipeline.py`.
2. Open `powerbi/Automated_Business_Dashboard.pbix` in **Power BI Desktop**.
3. Click **Refresh** on the Home ribbon (or press `F5`).
*(For cloud scheduled refresh via Power BI Gateway, see [docs/POWER_BI_REFRESH_GUIDE.md](docs/POWER_BI_REFRESH_GUIDE.md)).*

---

## ⏰ Automated Scheduling

### Windows Task Scheduler (Daily Automation)
To schedule the pipeline to run daily at 02:00 AM:

```powershell
.\scripts\schedule_task.ps1 -Time "02:00"
```
- To test the scheduled task: `.\scripts\schedule_task.ps1 -RunNow`
- To delete the task: `.\scripts\schedule_task.ps1 -Remove`

### Continuous Integration (GitHub Actions)
The repository includes `.github/workflows/automated_pipeline.yml` which automatically executes tests, verifies SQL syntax, and validates schema integrity on every commit, pull request, and daily on a scheduled cron.

---

## 🧪 Automated Testing

The project includes an automated test suite with **19 pytest tests** covering:
- Exact duplicate removal
- Cancellation filtering (`InvoiceNo` starting with `'C'`)
- Non-positive quantity and unit price exclusions
- Missing description imputation
- Date coercion and invalid timestamp dropping
- Revenue mathematical accuracy
- Transactional database loading & error rollback
- Idempotent duplicate file detection
- Pipeline dry-run and full end-to-end execution

Run the test suite:
```powershell
pytest tests/ -v
```

---

## 📄 License & Attribution

- **Dataset**: [UCI Machine Learning Repository - Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail)
- **Author**: Samruddhi Hole
- **License**: MIT License
