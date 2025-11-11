-- Portfolio Management System Reports
-- These queries demonstrate JOIN, NESTED, and AGGREGATE query patterns

-- ============================================================================
-- REPORT 1: Portfolio Details (JOIN QUERY)
-- ============================================================================
-- Multi-table join showing portfolio details with customer/employee and product information.
-- Joins: portfolios, customers, employees, transactions, products
-- ============================================================================
SELECT 
  p.P_ID AS portfolio_id,
  p.P_name AS portfolio_name,
  p.currency,
  p.risk_level,
  COALESCE(CONCAT(c.first_name, ' ', c.last_name), e.E_name) AS owner_name,
  CASE 
    WHEN p.C_ID IS NOT NULL THEN 'Customer'
    ELSE 'Employee'
  END AS owner_type,
  pr.Product_name AS product_name,
  pr.ticker_symbol,
  t.quantity,
  t.price_per_unit,
  t.transaction_date
FROM portfolios p
LEFT JOIN customers c ON p.C_ID = c.C_ID
LEFT JOIN employees e ON p.E_ID = e.E_ID
JOIN transactions t ON t.P_ID = p.P_ID
JOIN products pr ON pr.Product_ID = t.Product_ID
ORDER BY p.P_ID, t.transaction_date DESC;

-- ============================================================================
-- REPORT 2: Top Portfolios by Value (NESTED QUERY)
-- ============================================================================
-- Uses subquery to find portfolios with total value above average.
-- Shows portfolios that exceed the average portfolio value.
-- ============================================================================
SELECT 
  p.P_ID AS portfolio_id,
  p.P_name AS portfolio_name,
  COALESCE(CONCAT(c.first_name, ' ', c.last_name), e.E_name) AS owner_name,
  p.currency,
  COALESCE(SUM(t.quantity * t.price_per_unit), 0) AS total_value
FROM portfolios p
LEFT JOIN customers c ON p.C_ID = c.C_ID
LEFT JOIN employees e ON p.E_ID = e.E_ID
LEFT JOIN transactions t ON t.P_ID = p.P_ID
GROUP BY p.P_ID, p.P_name, owner_name, p.currency
HAVING COALESCE(SUM(t.quantity * t.price_per_unit), 0) > (
  SELECT AVG(portfolio_value)
  FROM (
    SELECT SUM(t2.quantity * t2.price_per_unit) AS portfolio_value
    FROM portfolios p2
    JOIN transactions t2 ON t2.P_ID = p2.P_ID
    GROUP BY p2.P_ID
  ) AS avg_values
)
ORDER BY total_value DESC;

-- ============================================================================
-- REPORT 3: Portfolio Performance Summary (AGGREGATE QUERY)
-- ============================================================================
-- Uses GROUP BY with multiple aggregate functions (SUM, COUNT, AVG, MAX).
-- Summarizes portfolio performance by currency and risk level.
-- ============================================================================
SELECT 
  p.currency,
  p.risk_level,
  COUNT(DISTINCT p.P_ID) AS portfolio_count,
  COUNT(t.T_ID) AS total_transactions,
  SUM(t.quantity * t.price_per_unit) AS total_invested,
  AVG(t.quantity * t.price_per_unit) AS avg_transaction_value,
  MAX(t.quantity * t.price_per_unit) AS max_transaction_value,
  SUM(t.commission_fee) AS total_commissions
FROM portfolios p
LEFT JOIN transactions t ON t.P_ID = p.P_ID
WHERE p.currency IS NOT NULL
GROUP BY p.currency, p.risk_level
HAVING COUNT(t.T_ID) > 0
ORDER BY p.currency, total_invested DESC;
