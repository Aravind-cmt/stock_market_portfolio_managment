-- =============================================================================
-- Stock Market Portfolio Management System
-- Database Schema Definition (MySQL 8.0+)
-- Adheres to 1NF, 2NF, 3NF/BCNF Relational Normalization
-- =============================================================================

CREATE DATABASE IF NOT EXISTS stock_portfolio_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE stock_portfolio_db;

-- -----------------------------------------------------------------------------
-- 1. Users Table
-- Stores user authentication credentials, contact profile, account status,
-- and simulated paper-trading wallet balance.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    cash_balance DECIMAL(15, 2) NOT NULL DEFAULT 100000.00,
    account_status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_cash_balance CHECK (cash_balance >= 0.00)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. Stocks Table
-- Master equity registry with current market price and sector classification.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(15) NOT NULL UNIQUE,
    company_name VARCHAR(120) NOT NULL,
    sector VARCHAR(60) NOT NULL,
    current_price DECIMAL(12, 2) NOT NULL,
    day_change DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    day_change_percent DECIMAL(6, 2) NOT NULL DEFAULT 0.00,
    high_52w DECIMAL(12, 2) DEFAULT NULL,
    low_52w DECIMAL(12, 2) DEFAULT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_stock_price CHECK (current_price > 0.00)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. Transactions Table
-- Immutable financial audit ledger recording every BUY and SELL order.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    transaction_type ENUM('BUY', 'SELL') NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    transaction_status ENUM('COMPLETED', 'FAILED', 'PENDING') NOT NULL DEFAULT 'COMPLETED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_tx_quantity CHECK (quantity > 0),
    CONSTRAINT chk_tx_price CHECK (price > 0.00),
    CONSTRAINT chk_tx_total CHECK (total_amount >= 0.00)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. Portfolio Table
-- Junction table resolving M:N relationship between Users and Stocks.
-- Maintains net quantity and dynamically updated weighted average buy price.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    total_quantity INT NOT NULL DEFAULT 0,
    average_buy_price DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_stock (user_id, stock_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_portfolio_qty CHECK (total_quantity >= 0),
    CONSTRAINT chk_portfolio_avg_price CHECK (average_buy_price >= 0.00)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. Watchlist Table
-- Tracks equities monitored by users with unique user-stock combination.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_watchlist_user_stock (user_id, stock_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. Roles Table
-- System roles for Role-Based Access Control (RBAC).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. User_Roles Table
-- Junction table assigning roles to users with auditing of assigner.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS User_Roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_by INT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. Audit_Log Table
-- Complete compliance and operational audit log tracking state transitions.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Audit_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    acting_user_id INT NULL,
    affected_user_id INT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NULL,
    previous_value TEXT NULL,
    new_value TEXT NULL,
    description TEXT,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acting_user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (affected_user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 9. Password_Reset Table
-- Secure token management for user password recovery workflows.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Password_Reset (
    reset_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reset_token_hash VARCHAR(255) NOT NULL,
    expiry_time DATETIME NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 10. Stock_Price_History Table
-- Historical stock price ticks for technical analysis and trend charts.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Stock_Price_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_hist_price CHECK (price > 0.00)
) ENGINE=InnoDB;
