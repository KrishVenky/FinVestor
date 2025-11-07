-- Report: KYC Contact Audit (JOIN + COUNT)
SELECT 
  CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
  d.aadhar_number AS aadhar_number,
  COUNT(ph.phone_id) AS phone_count
FROM customers c
JOIN customer_details d ON d.C_ID = c.C_ID
LEFT JOIN customer_phones ph ON ph.C_ID = c.C_ID
WHERE d.risk_tolerance IN ('low','medium','high')
GROUP BY c.C_ID, d.aadhar_number
ORDER BY phone_count DESC;

-- Report: Total AUM by Currency (SUM + GROUP BY + HAVING)
SELECT 
  p.currency AS currency,
  SUM(t.quantity * t.price_per_unit) AS total_invested
FROM portfolios p
JOIN transactions t ON t.P_ID = p.P_ID
GROUP BY p.currency
HAVING SUM(t.quantity * t.price_per_unit) > 0
ORDER BY total_invested DESC;

-- Report: Tech Sector Employee Investors (Nested Query)
SELECT DISTINCT e.E_name AS employee_name, e.job_title
FROM employees e
WHERE e.E_ID IN (
  SELECT p.E_ID
  FROM portfolios p
  JOIN transactions t ON t.P_ID = p.P_ID
  JOIN products pr ON pr.Product_ID = t.Product_ID
  WHERE pr.sector = 'Tech' AND p.E_ID IS NOT NULL
)
ORDER BY e.E_name ASC;