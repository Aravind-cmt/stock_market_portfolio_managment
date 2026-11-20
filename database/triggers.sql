-- =============================================================================
-- Stock Market Portfolio Management System
-- SQL Triggers Definition (MySQL 8.0+)
-- Ensures automated auditing, history tracking, and domain constraints.
-- =============================================================================

USE stock_portfolio_db;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Trigger: trg_after_stock_price_update
-- Fires AFTER UPDATE on Stocks. If current_price has changed,
-- automatically archives the price into Stock_Price_History.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_stock_price_update$$

CREATE TRIGGER trg_after_stock_price_update
AFTER UPDATE ON Stocks
FOR EACH ROW
BEGIN
    IF OLD.current_price <> NEW.current_price THEN
        INSERT INTO Stock_Price_History (stock_id, price, recorded_at)
        VALUES (NEW.stock_id, NEW.current_price, CURRENT_TIMESTAMP);
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 2. Trigger: trg_prevent_negative_cash
-- Fires BEFORE UPDATE on Users. Enforces business constraint: cash balance >= 0.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_negative_cash$$

CREATE TRIGGER trg_prevent_negative_cash
BEFORE UPDATE ON Users
FOR EACH ROW
BEGIN
    IF NEW.cash_balance < 0.00 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: Cash balance cannot drop below zero.';
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 3. Trigger: trg_prevent_negative_portfolio
-- Fires BEFORE UPDATE on Portfolio. Enforces: total_quantity >= 0.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_prevent_negative_portfolio$$

CREATE TRIGGER trg_prevent_negative_portfolio
BEFORE UPDATE ON Portfolio
FOR EACH ROW
BEGIN
    IF NEW.total_quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: Portfolio quantity cannot be negative.';
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- 4. Trigger: trg_after_user_registration
-- Fires AFTER INSERT on Users. Automatically assigns the default 'USER' role
-- and records a registration event into Audit_Log.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_after_user_registration$$

CREATE TRIGGER trg_after_user_registration
AFTER INSERT ON Users
FOR EACH ROW
BEGIN
    -- Assign default USER role (role_id = 3)
    INSERT INTO User_Roles (user_id, role_id, assigned_by, assigned_at)
    VALUES (NEW.user_id, 3, NULL, CURRENT_TIMESTAMP);

    -- Log to Audit_Log
    INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description)
    VALUES (
        NEW.user_id,
        NEW.user_id,
        'USER_REGISTRATION',
        'Users',
        NEW.user_id,
        NULL,
        CONCAT('Cash: ₹', NEW.cash_balance),
        CONCAT('New user registered: ', NEW.name, ' (', NEW.email, ')')
    );
END$$

DELIMITER ;
