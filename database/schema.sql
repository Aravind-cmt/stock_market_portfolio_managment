-- =============================================================================
-- Stock Market Portfolio Management System
-- Database Schema Definition (MySQL 8.0+)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS stock_portfolio_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE stock_portfolio_db;

-- Disable foreign key checks during schema creation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Stock_Price_History;
DROP TABLE IF EXISTS Password_Reset;
DROP TABLE IF EXISTS Audit_Log;
DROP TABLE IF EXISTS Watchlist;
DROP TABLE IF EXISTS Portfolio;
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS Stocks;
DROP TABLE IF EXISTS Admin;
DROP TABLE IF EXISTS Users;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. Users Table
-- Normalization: 1NF, 2NF, 3NF compliant. Stores user authentication, profile,
-- and paper-trading cash balance.
-- -----------------------------------------------------------------------------
CREATE TABLE Users (
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
-- Represents listed equities with current market price and sector classification.
-- -----------------------------------------------------------------------------
CREATE TABLE Stocks (
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
-- Records every BUY and SELL order executed by users (Financial Audit Trail).
-- -----------------------------------------------------------------------------
CREATE TABLE Transactions (
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
-- Represents aggregate holdings per user per stock.
-- Unique constraint ensures 1 row per user-stock pair.
-- -----------------------------------------------------------------------------
CREATE TABLE Portfolio (
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
-- Tracks stocks monitored by users.
-- -----------------------------------------------------------------------------
CREATE TABLE Watchlist (
    watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_watchlist_user_stock (user_id, stock_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. Admin Table
-- Administrative users with elevated privileges.
-- -----------------------------------------------------------------------------
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'SUPER_ADMIN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. Audit_Log Table
-- Security and compliance audit trail tracking all state modifications.
-- -----------------------------------------------------------------------------
CREATE TABLE Audit_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NULL,
    action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. Password_Reset Table
-- Secure token management for password recovery workflow.
-- -----------------------------------------------------------------------------
CREATE TABLE Password_Reset (
    reset_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reset_token_hash VARCHAR(255) NOT NULL,
    expiry_time DATETIME NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 9. Stock_Price_History Table
-- Historical stock prices for technical analysis and trend charts.
-- -----------------------------------------------------------------------------
CREATE TABLE Stock_Price_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_hist_price CHECK (price > 0.00)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Performance Indexes for Fast Lookups
-- -----------------------------------------------------------------------------
CREATE INDEX idx_stocks_symbol ON Stocks(symbol);
CREATE INDEX idx_stocks_sector ON Stocks(sector);
CREATE INDEX idx_transactions_user ON Transactions(user_id);
CREATE INDEX idx_transactions_stock ON Transactions(stock_id);
CREATE INDEX idx_transactions_date ON Transactions(transaction_date);
CREATE INDEX idx_portfolio_user ON Portfolio(user_id);
CREATE INDEX idx_watchlist_user ON Watchlist(user_id);
CREATE INDEX idx_price_history_stock_date ON Stock_Price_History(stock_id, recorded_at);
CREATE INDEX idx_audit_log_timestamp ON Audit_Log(action_timestamp);
