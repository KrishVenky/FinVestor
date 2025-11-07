-- Ensure correct database is selected
-- USE findb;

DELIMITER $$

-- Function: Calculate_Age(dob DATE) -> INT years
DROP FUNCTION IF EXISTS Calculate_Age $$
CREATE FUNCTION Calculate_Age(dob DATE)
RETURNS INT
DETERMINISTIC
BEGIN
  IF dob IS NULL THEN
    RETURN NULL;
  END IF;
  RETURN TIMESTAMPDIFF(YEAR, dob, CURDATE());
END $$

-- Procedure: Process_Trade
-- Inserts a transaction with commission_fee computed as quantity * price_per_unit * commission_rate
DROP PROCEDURE IF EXISTS Process_Trade $$
CREATE PROCEDURE Process_Trade(
  IN in_p_id INT,
  IN in_product_id INT,
  IN in_quantity INT,
  IN in_price_per_unit DECIMAL(10,2),
  IN in_commission_rate DECIMAL(8,4)
)
BEGIN
  DECLARE fee DECIMAL(8,2);
  IF in_commission_rate IS NULL THEN
    SET in_commission_rate = 0;
  END IF;
  SET fee = ROUND(in_quantity * in_price_per_unit * in_commission_rate, 2);
  INSERT INTO transactions(P_ID, Product_ID, quantity, price_per_unit, transaction_date, commission_fee)
  VALUES (in_p_id, in_product_id, in_quantity, in_price_per_unit, NOW(), fee);
END $$

-- Trigger: before_employee_insert
DROP TRIGGER IF EXISTS before_employee_insert $$
CREATE TRIGGER before_employee_insert
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
  IF NEW.specialization IS NULL OR NEW.specialization = '' THEN
    SET NEW.specialization = 'General Support';
  END IF;
END $$

DELIMITER ;


