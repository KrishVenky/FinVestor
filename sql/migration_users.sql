-- Migration script to add users table for authentication
-- Run this after the base schema is created

CREATE TABLE IF NOT EXISTS users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('regular', 'employee', 'manager', 'superadmin') NOT NULL DEFAULT 'regular',
  C_ID INT NULL,
  E_ID INT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_user_customer FOREIGN KEY (C_ID) REFERENCES customers(C_ID) ON DELETE CASCADE,
  CONSTRAINT fk_user_employee FOREIGN KEY (E_ID) REFERENCES employees(E_ID) ON DELETE CASCADE,
  CONSTRAINT chk_user_has_entity CHECK ((C_ID IS NOT NULL) OR (E_ID IS NOT NULL))
);

-- Create indexes for faster lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_c_id ON users(C_ID);
CREATE INDEX idx_users_e_id ON users(E_ID);

