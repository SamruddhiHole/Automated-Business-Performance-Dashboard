-- ==============================================================================
-- Automated Business Performance Dashboard - SQL Analytics Queries
-- ==============================================================================

-- 1. Executive Summary KPIs
SELECT
    ROUND(SUM(Revenue), 2) AS Total_Revenue,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    COUNT(DISTINCT CustomerID) AS Identified_Customers,
    COUNT(DISTINCT StockCode) AS Unique_Products,
    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS Average_Order_Value,
    SUM(Quantity) AS Total_Quantity_Sold
FROM sales;

-- 2. Monthly Revenue and Order Growth
SELECT
    SUBSTR(InvoiceDate, 1, 7) AS YearMonth,
    ROUND(SUM(Revenue), 2) AS Monthly_Revenue,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    SUM(Quantity) AS Total_Quantity,
    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS Average_Order_Value
FROM sales
GROUP BY YearMonth
ORDER BY YearMonth;

-- 3. Top 10 Countries by Revenue Performance
SELECT
    Country,
    ROUND(SUM(Revenue), 2) AS Total_Revenue,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    COUNT(DISTINCT CustomerID) AS Customer_Count,
    ROUND(SUM(Revenue) * 100.0 / (SELECT SUM(Revenue) FROM sales), 2) AS Revenue_Share_Pct
FROM sales
GROUP BY Country
ORDER BY Total_Revenue DESC
LIMIT 10;

-- 4. Top 10 Merchandise Products by Revenue (Excluding Postage & Non-Merchandise)
SELECT
    StockCode,
    Description,
    SUM(Quantity) AS Total_Quantity_Sold,
    ROUND(SUM(Revenue), 2) AS Total_Revenue,
    ROUND(AVG(UnitPrice), 2) AS Avg_Unit_Price
FROM sales
WHERE UPPER(TRIM(Description)) NOT LIKE '%POSTAGE%'
  AND UPPER(TRIM(Description)) NOT LIKE '%POST%'
  AND UPPER(TRIM(Description)) <> 'MANUAL'
  AND UPPER(TRIM(Description)) <> 'DISCOUNT'
  AND UPPER(TRIM(Description)) <> 'BANK CHARGES'
GROUP BY StockCode, Description
ORDER BY Total_Revenue DESC
LIMIT 10;

-- 5. Top 10 Customers by Revenue (Identified Customers Only)
SELECT
    CustomerID,
    Country,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    SUM(Quantity) AS Total_Quantity_Purchased,
    ROUND(SUM(Revenue), 2) AS Total_Spend,
    ROUND(SUM(Revenue) / COUNT(DISTINCT InvoiceNo), 2) AS Avg_Order_Spend
FROM sales
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID, Country
ORDER BY Total_Spend DESC
LIMIT 10;

-- 6. Day of Week Sales Distribution
-- SQLite strftime('%w', InvoiceDate): 0 = Sunday, 1 = Monday, ..., 6 = Saturday
SELECT
    CASE CAST(strftime('%w', InvoiceDate) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS Day_Name,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders,
    SUM(Quantity) AS Total_Quantity,
    ROUND(SUM(Revenue), 2) AS Total_Revenue
FROM sales
GROUP BY strftime('%w', InvoiceDate)
ORDER BY Total_Revenue DESC;

-- 7. Customer Purchase Frequency Distribution
WITH CustomerOrders AS (
    SELECT
        CustomerID,
        COUNT(DISTINCT InvoiceNo) AS Order_Count
    FROM sales
    WHERE CustomerID IS NOT NULL
    GROUP BY CustomerID
)
SELECT
    CASE
        WHEN Order_Count = 1 THEN '1 Order (One-Time)'
        WHEN Order_Count BETWEEN 2 AND 5 THEN '2-5 Orders (Occasional)'
        WHEN Order_Count BETWEEN 6 AND 10 THEN '6-10 Orders (Frequent)'
        ELSE '10+ Orders (VIP)'
    END AS Frequency_Bucket,
    COUNT(CustomerID) AS Customer_Count,
    ROUND(COUNT(CustomerID) * 100.0 / (SELECT COUNT(*) FROM CustomerOrders), 2) AS Pct_Of_Customers
FROM CustomerOrders
GROUP BY Frequency_Bucket
ORDER BY Customer_Count DESC;
