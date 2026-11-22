# Automated-Business-Performance-Dashboard
# Automated Business Performance Dashboard

## Project Overview

The **Automated Business Performance Dashboard** is a data analytics project developed to analyze online retail sales data and transform raw transaction records into meaningful business insights.

The project uses Python for data cleaning and exploratory data analysis, SQL for database management and querying, and Power BI for creating an interactive business dashboard.

The main objective is to help businesses understand sales performance, customer behaviour, product performance, and revenue trends.

## Project Objectives

- Clean and prepare raw retail transaction data.
- Perform exploratory data analysis (EDA).
- Store and analyze cleaned data using SQL.
- Identify important business KPIs.
- Analyze sales, customers, countries, and products.
- Build an interactive Power BI dashboard.
- Present useful insights through visualizations.

## Tools and Technologies

| Tool | Purpose |
|---|---|
| Python | Data cleaning and EDA |
| Pandas | Data manipulation |
| SQL | Database management and analysis |
| SQLite | Storing sales data |
| Power BI | Interactive dashboards |
| DAX | Measures and KPI calculations |
| Excel/CSV | Dataset handling |

## Dataset

**Dataset:** Online Retail Dataset

**Source:** UCI Machine Learning Repository

The dataset contains online retail transactions from December 2010 to December 2011.

Original dataset:
- 541,909 transaction records
- 8 columns

Cleaned dataset:
- 524,878 valid sales records
- 9 columns

Important columns include:
- InvoiceNo
- StockCode
- Description
- Quantity
- InvoiceDate
- UnitPrice
- CustomerID
- Country
- Revenue

Revenue was calculated as:

`Revenue = Quantity × UnitPrice`

## Data Cleaning and Preparation

The following cleaning operations were performed using Python:

1. Removed duplicate records.
2. Excluded cancelled invoices.
3. Removed records with zero or negative quantities.
4. Removed records with zero or negative unit prices.
5. Filled missing product descriptions with "Unknown Product".
6. Retained missing CustomerID records in the sales dataset, but excluded them from identified customer counts and customer-level analysis.
7. Created a Revenue column.

The cleaned dataset was exported as `cleaned_sales.csv`.

## SQL Database

The cleaned dataset was imported into an SQLite database named `retail_business.db`.

A table named `sales` was created.

SQL was used to:
- Calculate total revenue.
- Count unique orders.
- Analyze customer purchases.
- Identify top-performing products.
- Compare sales across countries.
- Analyze monthly sales performance.

## Power BI Dashboard

The Power BI report contains four interactive pages.

### 1. Business Overview
- Total Revenue
- Total Orders
- Average Order Value
- Total Customers
- Monthly Revenue Trend
- Top 10 Countries by Revenue
- Top 10 Products by Revenue
- Top 10 Customers by Revenue

### 2. Sales Analysis
- Monthly Orders Trend
- Daily Revenue Trend
- Revenue by Day of Week
- Monthly Quantity Sold
- Sales Performance Summary

### 3. Customer Analysis
- Total Customers
- Total Revenue
- Total Orders
- Average Revenue per Customer
- Top 10 Customers by Revenue
- Customer Segmentation
- Orders per Customer
- Customer Summary

### 4. Product Analysis
- Total Products
- Total Revenue
- Total Quantity Sold
- Average Unit Price
- Top 10 Products by Revenue
- Top 10 Products by Quantity Sold
- Monthly Product Revenue Trend
- Product Performance Summary

## Key Business KPIs

| KPI | Result |
|---|---:|
| Total Revenue | £10,642,110.80 |
| Total Orders | 19,960 |
| Identified Customers | 4,338 |
| Average Order Value | £533.17 |
| Unique Products | 3,922 |
| Top Revenue Country | United Kingdom |

## Key Findings

- The United Kingdom is the leading country by revenue.
- The dataset contains 4,338 customers with identified CustomerIDs.
- Product and customer rankings help identify important contributors to sales.
- Monthly trends help understand changes in business performance.
- Customer segmentation helps compare customers based on their revenue contribution.

## Important Data Limitations

- December 2011 is a partial month, with data ending on December 9.
- Total Revenue represents gross positive sales and includes service and adjustment entries present in the cleaned dataset.
- Customer-level analysis excludes transactions with missing CustomerIDs.
- Merchandise product rankings exclude postage and manual entries.

## Project Workflow

1. Data collection
2. Data cleaning using Python
3. Exploratory data analysis
4. Database creation using SQLite
5. SQL analysis
6. Power BI data import
7. DAX measure creation
8. Interactive dashboard development
9. Business insights and reporting

## Conclusion

This project demonstrates the complete data analytics workflow, from raw dataset preparation to interactive business reporting.

By combining Python, SQL, and Power BI, the project transforms retail transaction data into useful information that can support business decision-making.

## Author

**Samruddhi Hole**

**Project:** Automated Business Performance Dashboard

**Technologies:** Python | SQL | SQLite | Power BI | DAX
