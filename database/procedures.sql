-- =============================================================================
-- Stock Market Portfolio Management System
-- Stored Procedures Definition (MySQL 8.0+)
-- Implements ACID compliant Buy/Sell transactions with row locking.
-- =============================================================================

USE stock_portfolio_db;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Procedure: sp_buy_stock
-- Executes a BUY order inside an ACID transaction.
-- Locks user balance, verifies sufficient funds, deducts cash, records
-- transaction, updates weighted average buy price in Portfolio, and audits.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_buy_stock$$

CREATE PROCEDURE sp_buy_stock(
    IN p_user_id INT,
    IN p_stock_id INT,
    IN p_quantity INT,
    OUT p_status VARCHAR(20),
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_cash DECIMAL(15, 2);
    DECLARE v_price DECIMAL(12, 2);
    DECLARE v_total_cost DECIMAL(15, 2);
    DECLARE v_account_status VARCHAR(20);
    DECLARE v_existing_qty INT DEFAULT 0;
    DECLARE v_existing_avg DECIMAL(12, 2) DEFAULT 0.00;
    DECLARE v_new_avg DECIMAL(12, 2);
    DECLARE v_tx_id INT;

    -- Error handler for unexpected SQL exceptions
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Database error occurred during buy execution. Transaction rolled back.';
    END;

    -- Basic input validation
    IF p_quantity <= 0 THEN
        SET p_status = 'ERROR';
        SET p_message = 'Quantity must be greater than zero.';
        LEAVE proc_label;
    END IF;

    -- Begin ACID Transaction
    START TRANSACTION;

    -- Lock and verify User
    SELECT cash_balance, account_status 
    INTO v_cash, v_account_status
    FROM Users 
    WHERE user_id = p_user_id 
    FOR UPDATE;

    IF v_account_status IS NULL THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'User account not found.';
        LEAVE proc_label;
    END IF;

    IF v_account_status <> 'ACTIVE' THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'User account is not active.';
        LEAVE proc_label;
    END IF;

    -- Lock and verify Stock
    SELECT current_price 
    INTO v_price
    FROM Stocks 
    WHERE stock_id = p_stock_id;

    IF v_price IS NULL THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Stock not found in market registry.';
        LEAVE proc_label;
    END IF;

    -- Calculate total cost
    SET v_total_cost = ROUND(v_price * p_quantity, 2);

    -- Validate cash balance
    IF v_cash < v_total_cost THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = CONCAT('Insufficient cash balance. Required: ₹', v_total_cost, ', Available: ₹', v_cash);
        LEAVE proc_label;
    END IF;

    -- 1. Deduct cash from user wallet
    UPDATE Users 
    SET cash_balance = cash_balance - v_total_cost 
    WHERE user_id = p_user_id;

    -- 2. Insert BUY transaction
    INSERT INTO Transactions (
        user_id, stock_id, transaction_type, quantity, price, total_amount, 
        transaction_date, transaction_time, transaction_status
    ) VALUES (
        p_user_id, p_stock_id, 'BUY', p_quantity, v_price, v_total_cost, 
        CURDATE(), CURTIME(), 'COMPLETED'
    );
    SET v_tx_id = LAST_INSERT_ID();

    -- 3. Update or Insert Portfolio holding
    SELECT total_quantity, average_buy_price 
    INTO v_existing_qty, v_existing_avg
    FROM Portfolio 
    WHERE user_id = p_user_id AND stock_id = p_stock_id 
    FOR UPDATE;

    IF v_existing_qty > 0 THEN
        -- Recalculate weighted average purchase price:
        -- ((old_qty * old_avg) + (new_qty * new_price)) / (old_qty + new_qty)
        SET v_new_avg = ROUND(((v_existing_qty * v_existing_avg) + (p_quantity * v_price)) / (v_existing_qty + p_quantity), 2);
        
        UPDATE Portfolio 
        SET total_quantity = total_quantity + p_quantity,
            average_buy_price = v_new_avg,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = p_user_id AND stock_id = p_stock_id;
    ELSE
        INSERT INTO Portfolio (user_id, stock_id, total_quantity, average_buy_price)
        VALUES (p_user_id, p_stock_id, p_quantity, v_price);
    END IF;

    -- 4. Record Audit Log
    INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
    VALUES (
        p_user_id, 'BUY_ORDER', 'Transactions', v_tx_id, 
        CONCAT('Successfully bought ', p_quantity, ' shares at ₹', v_price, '. Total: ₹', v_total_cost)
    );

    COMMIT;
    SET p_status = 'SUCCESS';
    SET p_message = CONCAT('Successfully purchased ', p_quantity, ' shares at ₹', v_price);
END$$

-- -----------------------------------------------------------------------------
-- 2. Procedure: sp_sell_stock
-- Executes a SELL order inside an ACID transaction.
-- Locks portfolio row, validates available shares, prevents overselling,
-- credits cash, updates/removes holding, calculates realized P&L, and audits.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_sell_stock$$

CREATE PROCEDURE sp_sell_stock(
    IN p_user_id INT,
    IN p_stock_id INT,
    IN p_quantity INT,
    OUT p_status VARCHAR(20),
    OUT p_message VARCHAR(255),
    OUT p_realized_pnl DECIMAL(12, 2)
)
proc_label: BEGIN
    DECLARE v_price DECIMAL(12, 2);
    DECLARE v_total_revenue DECIMAL(15, 2);
    DECLARE v_account_status VARCHAR(20);
    DECLARE v_port_id INT;
    DECLARE v_existing_qty INT;
    DECLARE v_avg_buy_price DECIMAL(12, 2);
    DECLARE v_tx_id INT;

    SET p_realized_pnl = 0.00;

    -- Error handler
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Database error occurred during sell execution. Transaction rolled back.';
    END;

    -- Basic input validation
    IF p_quantity <= 0 THEN
        SET p_status = 'ERROR';
        SET p_message = 'Quantity must be greater than zero.';
        LEAVE proc_label;
    END IF;

    -- Begin ACID Transaction
    START TRANSACTION;

    -- Validate user
    SELECT account_status INTO v_account_status
    FROM Users WHERE user_id = p_user_id;

    IF v_account_status IS NULL OR v_account_status <> 'ACTIVE' THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'User account is invalid or inactive.';
        LEAVE proc_label;
    END IF;

    -- Lock and verify Portfolio row
    SELECT portfolio_id, total_quantity, average_buy_price
    INTO v_port_id, v_existing_qty, v_avg_buy_price
    FROM Portfolio
    WHERE user_id = p_user_id AND stock_id = p_stock_id
    FOR UPDATE;

    IF v_port_id IS NULL OR v_existing_qty < p_quantity THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = CONCAT('Insufficient shares owned. You currently hold ', COALESCE(v_existing_qty, 0), ' shares.');
        LEAVE proc_label;
    END IF;

    -- Fetch current stock price
    SELECT current_price INTO v_price
    FROM Stocks WHERE stock_id = p_stock_id;

    IF v_price IS NULL THEN
        ROLLBACK;
        SET p_status = 'ERROR';
        SET p_message = 'Stock not found in market registry.';
        LEAVE proc_label;
    END IF;

    -- Calculations
    SET v_total_revenue = ROUND(v_price * p_quantity, 2);
    SET p_realized_pnl = ROUND((v_price - v_avg_buy_price) * p_quantity, 2);

    -- 1. Credit cash to user balance
    UPDATE Users 
    SET cash_balance = cash_balance + v_total_revenue 
    WHERE user_id = p_user_id;

    -- 2. Insert SELL transaction
    INSERT INTO Transactions (
        user_id, stock_id, transaction_type, quantity, price, total_amount, 
        transaction_date, transaction_time, transaction_status
    ) VALUES (
        p_user_id, p_stock_id, 'SELL', p_quantity, v_price, v_total_revenue, 
        CURDATE(), CURTIME(), 'COMPLETED'
    );
    SET v_tx_id = LAST_INSERT_ID();

    -- 3. Update Portfolio holding
    IF v_existing_qty = p_quantity THEN
        DELETE FROM Portfolio WHERE portfolio_id = v_port_id;
    ELSE
        UPDATE Portfolio 
        SET total_quantity = total_quantity - p_quantity,
            updated_at = CURRENT_TIMESTAMP
        WHERE portfolio_id = v_port_id;
    END IF;

    -- 4. Record Audit Log
    INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
    VALUES (
        p_user_id, 'SELL_ORDER', 'Transactions', v_tx_id, 
        CONCAT('Sold ', p_quantity, ' shares at ₹', v_price, '. Total proceeds: ₹', v_total_revenue, '. Realized P&L: ₹', p_realized_pnl)
    );

    COMMIT;
    SET p_status = 'SUCCESS';
    SET p_message = CONCAT('Successfully sold ', p_quantity, ' shares at ₹', v_price, '. Realized P&L: ₹', p_realized_pnl);
END$$

-- -----------------------------------------------------------------------------
-- 3. Procedure: sp_update_stock_price
-- Allows Admin to update a stock's price, calculating change & storing history.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_update_stock_price$$

CREATE PROCEDURE sp_update_stock_price(
    IN p_stock_id INT,
    IN p_new_price DECIMAL(12, 2),
    OUT p_status VARCHAR(20),
    OUT p_message VARCHAR(255)
)
proc_label: BEGIN
    DECLARE v_old_price DECIMAL(12, 2);
    DECLARE v_change DECIMAL(10, 2);
    DECLARE v_change_pct DECIMAL(6, 2);

    IF p_new_price <= 0.00 THEN
        SET p_status = 'ERROR';
        SET p_message = 'Stock price must be greater than zero.';
        LEAVE proc_label;
    END IF;

    SELECT current_price INTO v_old_price
    FROM Stocks WHERE stock_id = p_stock_id;

    IF v_old_price IS NULL THEN
        SET p_status = 'ERROR';
        SET p_message = 'Stock ID not found.';
        LEAVE proc_label;
    END IF;

    SET v_change = ROUND(p_new_price - v_old_price, 2);
    SET v_change_pct = ROUND((v_change / v_old_price) * 100, 2);

    UPDATE Stocks 
    SET current_price = p_new_price,
        day_change = v_change,
        day_change_percent = v_change_pct,
        updated_at = CURRENT_TIMESTAMP
    WHERE stock_id = p_stock_id;

    INSERT INTO Stock_Price_History (stock_id, price, recorded_at)
    VALUES (p_stock_id, p_new_price, CURRENT_TIMESTAMP);

    INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
    VALUES (
        NULL, 'PRICE_UPDATE', 'Stocks', p_stock_id,
        CONCAT('Price updated from ₹', v_old_price, ' to ₹', p_new_price, ' (', v_change_pct, '%)')
    );

    SET p_status = 'SUCCESS';
    SET p_message = CONCAT('Price updated successfully to ₹', p_new_price);
END$$

-- -----------------------------------------------------------------------------
-- 4. Procedure: sp_get_user_portfolio
-- Returns active holdings for a specific user.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_user_portfolio$$

CREATE PROCEDURE sp_get_user_portfolio(
    IN p_user_id INT
)
BEGIN
    SELECT 
        p.portfolio_id,
        s.stock_id,
        s.symbol,
        s.company_name,
        s.sector,
        p.total_quantity,
        p.average_buy_price,
        s.current_price,
        ROUND(p.total_quantity * p.average_buy_price, 2) AS total_investment,
        ROUND(p.total_quantity * s.current_price, 2) AS current_value,
        ROUND((p.total_quantity * s.current_price) - (p.total_quantity * p.average_buy_price), 2) AS profit_loss,
        ROUND(
            CASE 
                WHEN p.average_buy_price > 0 THEN 
                    (((s.current_price - p.average_buy_price) / p.average_buy_price) * 100)
                ELSE 0.00 
            END, 2
        ) AS profit_loss_percent,
        p.updated_at
    FROM Portfolio p
    JOIN Stocks s ON p.stock_id = s.stock_id
    WHERE p.user_id = p_user_id AND p.total_quantity > 0
    ORDER BY current_value DESC;
END$$

DELIMITER ;
