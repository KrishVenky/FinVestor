-- Schema DDL for Financial Investment Platform (aligns with current DB)

CREATE TABLE IF NOT EXISTS customers (
  C_ID INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  date_of_birth DATE NULL,
  address VARCHAR(255) NULL
);

CREATE TABLE IF NOT EXISTS customer_details (
  C_ID INT PRIMARY KEY,
  ssn VARCHAR(20) UNIQUE NULL,
  pan_number VARCHAR(20) NOT NULL UNIQUE,
  aadhar_number VARCHAR(20) NOT NULL UNIQUE,
  occupation VARCHAR(100) NULL,
  annual_income DECIMAL(15,2) NULL,
  risk_tolerance ENUM('low','medium','high') NULL,
  CONSTRAINT fk_cd_customer FOREIGN KEY (C_ID) REFERENCES customers(C_ID)
);

CREATE TABLE IF NOT EXISTS customer_phones (
  phone_id INT PRIMARY KEY AUTO_INCREMENT,
  C_ID INT NOT NULL,
  phone_number VARCHAR(20) NOT NULL,
  phone_type ENUM('mobile','home','work') NULL,
  CONSTRAINT fk_cp_customer FOREIGN KEY (C_ID) REFERENCES customers(C_ID)
);

CREATE TABLE IF NOT EXISTS customer_emails (
  email_id INT PRIMARY KEY AUTO_INCREMENT,
  C_ID INT NOT NULL,
  email_address VARCHAR(100) NOT NULL UNIQUE,
  email_type ENUM('personal','work','other') NULL,
  CONSTRAINT fk_ce_customer FOREIGN KEY (C_ID) REFERENCES customers(C_ID)
);

CREATE TABLE IF NOT EXISTS employees (
  E_ID INT PRIMARY KEY AUTO_INCREMENT,
  E_name VARCHAR(100) NOT NULL,
  job_title VARCHAR(100) NULL,
  hire_date DATE NULL,
  specialization VARCHAR(255) NULL,
  manager_id INT NULL,
  CONSTRAINT fk_emp_manager FOREIGN KEY (manager_id) REFERENCES employees(E_ID)
);

CREATE TABLE IF NOT EXISTS products (
  Product_ID INT PRIMARY KEY AUTO_INCREMENT,
  Product_name VARCHAR(255) NOT NULL,
  ticker_symbol VARCHAR(10) NOT NULL UNIQUE,
  current_price DECIMAL(10,2) NULL,
  sector VARCHAR(100) NULL
);

CREATE TABLE IF NOT EXISTS portfolios (
  P_ID INT PRIMARY KEY AUTO_INCREMENT,
  P_name VARCHAR(100) NOT NULL,
  creation_date DATE NOT NULL,
  risk_level ENUM('low','medium','high') NULL,
  currency VARCHAR(10) NULL,
  C_ID INT NULL,
  E_ID INT NULL,
  CONSTRAINT fk_p_customer FOREIGN KEY (C_ID) REFERENCES customers(C_ID),
  CONSTRAINT fk_p_employee FOREIGN KEY (E_ID) REFERENCES employees(E_ID)
  -- Application enforces at least one of C_ID or E_ID via validation
);

CREATE TABLE IF NOT EXISTS transactions (
  T_ID INT PRIMARY KEY AUTO_INCREMENT,
  P_ID INT NOT NULL,
  Product_ID INT NOT NULL,
  quantity INT NOT NULL,
  price_per_unit DECIMAL(10,2) NOT NULL,
  transaction_date DATETIME NOT NULL,
  commission_fee DECIMAL(8,2) NULL,
  CONSTRAINT fk_t_portfolio FOREIGN KEY (P_ID) REFERENCES portfolios(P_ID),
  CONSTRAINT fk_t_product FOREIGN KEY (Product_ID) REFERENCES products(Product_ID)
);