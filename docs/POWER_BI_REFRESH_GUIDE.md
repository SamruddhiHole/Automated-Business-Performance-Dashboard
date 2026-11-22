# Power BI Dashboard & Refresh Guide

This document explains the design, data architecture, DAX metrics, and data refresh workflows for the **Automated Business Performance Dashboard** (`powerbi/Automated_Business_Dashboard.pbix`).

---

## 1. Dashboard Structure & Pages

The dashboard consists of four report pages:

### Page 1: Business Overview
- **Executive KPI Cards**: Total Revenue (£10.64M), Average Order Value (£533.17), Total Orders (19.96K), Total Identified Customers (4.34K).
- **Monthly Revenue Trend**: Line chart analyzing revenue progression across 2010–2011.
- **Top 10 Countries by Revenue**: Clustered bar chart showing geographic market distribution.
- **Top 10 Products by Revenue**: Clustered bar chart highlighting top-selling merchandise.
- **Top 10 Customers by Revenue**: Detailed summary table showing customer spend and order volume.
- **Interactive Slicers**: Slicers for `Year`, `YearMonth`, and `Country`.

### Page 2: Sales Analysis
- **KPI Cards**: Total Revenue, Total Orders, Total Quantity Sold, Average Order Value.
- **Monthly Orders Trend**: Line chart of transaction volume per month.
- **Daily Sales Progression**: Daily revenue trends.
- **Revenue by Day of Week**: Bar chart identifying peak sales days (e.g. Thursday and Tuesday).
- **Monthly Quantity Sold**: Column chart tracking units moved per month.
- **Sales Performance Summary**: Granular table comparing monthly revenue, orders, quantity, and AOV.

### Page 3: Customer Analysis
- **KPI Cards**: Total Identified Customers, Average Revenue per Customer, Total Revenue, Total Orders.
- **Top 10 Customer Spend**: Bar chart ranking top spending accounts.
- **Customer Segmentation**: Donut chart segmenting customers by purchasing tier.
- **Orders per Customer**: Column chart displaying order frequency distribution (1 order vs 2–5 vs 6–10 vs VIP).
- **Top Customer Summary**: Multi-column breakdown of customer performance.

### Page 4: Product Analysis
- **KPI Cards**: Total Products (3,922), Total Quantity Sold (5.57M), Average Unit Price (£3.26), Total Revenue.
- **Top 10 Products by Revenue**: Top merchandise earners (excluding postage/manual fees).
- **Top 10 Products by Quantity Sold**: High-volume unit drivers.
- **Product Revenue Trend**: Monthly product revenue trajectory.
- **Product Performance Summary Table**: StockCode, Description, Total Revenue, Total Quantity, and Average Unit Price.

---

## 2. Key DAX Measures

The report defines standard DAX measures built on `cleaned_sales`:

```dax
-- Total Gross Revenue
Total Revenue = SUM(cleaned_sales[Revenue])

-- Total Valid Orders
Total Orders = DISTINCTCOUNT(cleaned_sales[InvoiceNo])

-- Total Identified Customers (Excludes blank/null IDs)
Total Customers = 
CALCULATE(
    DISTINCTCOUNT(cleaned_sales[CustomerID]),
    cleaned_sales[CustomerID] <> BLANK()
)

-- Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Revenue], [Total Orders], 0)

-- Total Products Count
Total Products = DISTINCTCOUNT(cleaned_sales[StockCode])

-- Total Quantity Sold
Total Quantity = SUM(cleaned_sales[Quantity])

-- Average Revenue per Customer
Average Revenue per Customer = 
DIVIDE([Total Revenue], [Total Customers], 0)
```

---

## 3. Data Refresh Options

### Option A: Standard Desktop Refresh (Recommended for Local Use)
1. Execute the automated data pipeline:
   ```powershell
   python python/automated_pipeline.py
   ```
2. Open `powerbi/Automated_Business_Dashboard.pbix` in **Power BI Desktop**.
3. In the top ribbon on the **Home** tab, click **Refresh** (or press `F5`).
4. Power BI will read the updated `data/processed/cleaned_sales.csv` and recompute all DAX measures, charts, and tables instantly.
5. Save the report.

### Option B: Power BI Service Scheduled Cloud Refresh (Enterprise / Advanced)
To schedule unattended refreshes in the Power BI Cloud Service:
1. **Publish**: In Power BI Desktop, click **File** $\rightarrow$ **Publish** $\rightarrow$ **Publish to Power BI** and select your workspace.
2. **On-Premises Data Gateway**:
   - Because `cleaned_sales.csv` lives on a local disk / OneDrive path, install the **Power BI On-premises Data Gateway (Personal or Standard Mode)** on the host machine.
   - Register the gateway with your Power BI Service account.
3. **Configure Dataset Settings**:
   - Navigate to [app.powerbi.com](https://app.powerbi.com), locate the dataset, and open **Settings** $\rightarrow$ **Gateway Connection**.
   - Map the file path to your active gateway.
4. **Schedule Refresh**:
   - Under **Scheduled Refresh**, set the refresh schedule (e.g., Daily at 03:00 AM, following the 02:00 AM Python pipeline).
   
*Note: Local Python scripts cannot directly force an open Power BI Desktop window to refresh without GUI automation; using the standard Desktop Refresh button or Power BI Service Gateway is the industry-standard architecture.*
