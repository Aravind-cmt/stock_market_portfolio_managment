-- =============================================================================
-- Stock Market Portfolio Management System
-- Comprehensive Demonstration Queries for 26 DBMS Lab Requirements (MySQL 8.0+)
-- =============================================================================

USE stock_portfolio_db;

-- -----------------------------------------------------------------------------
-- 1. Primary Keys & Foreign Keys
-- -----------------------------------------------------------------------------
SELECT 
    t.transaction_id,
    u.user_id,
    u.name AS investor_name,
    s.stock_id,
    s.symbol,
    t.transaction_type,
    t.quantity,
    t.price,
    t.total_amount
FROM Transactions t
JOIN Users u ON t.user_id = u.user_id
JOIN Stocks s ON t.stock_id = s.stock_id
ORDER BY t.transaction_id DESC
LIMIT 5;

-- -----------------------------------------------------------------------------
-- 2. One-to-Many & Many-to-Many Relationships
-- -----------------------------------------------------------------------------
-- M:N Users to Stocks resolved through Portfolio junction:
SELECT 
    u.name AS investor,
    GROUP_CONCAT(DISTINCT s.symbol ORDER BY s.symbol SEPARATOR ', ') AS held_stocks,
    COUNT(p.stock_id) AS distinct_stocks_count,
    SUM(p.total_quantity) AS total_units_owned
FROM Users u
JOIN Portfolio p ON u.user_id = p.user_id
JOIN Stocks s ON p.stock_id = s.stock_id
WHERE p.total_quantity > 0
GROUP BY u.user_id, u.name;

-- -----------------------------------------------------------------------------
-- 3. SQL JOIN Operations: INNER JOIN, LEFT JOIN, RIGHT JOIN
-- -----------------------------------------------------------------------------
-- A. INNER JOIN: Active investors with holdings
SELECT u.name, s.symbol, p.total_quantity, p.average_buy_price
FROM Users u
INNER JOIN Portfolio p ON u.user_id = p.user_id
INNER JOIN Stocks s ON p.stock_id = s.stock_id;

-- B. LEFT JOIN: All equities with optional investor counts
SELECT s.symbol, s.company_name, COUNT(p.user_id) AS investor_count
FROM Stocks s
LEFT JOIN Portfolio p ON s.stock_id = p.stock_id AND p.total_quantity > 0
GROUP BY s.stock_id, s.symbol, s.company_name
ORDER BY investor_count DESC;

-- C. RIGHT JOIN: Watchlist entries joined with Stocks catalog
SELECT w.watchlist_id, u.name, s.symbol, s.current_price
FROM Watchlist w
RIGHT JOIN Stocks s ON w.stock_id = s.stock_id
LEFT JOIN Users u ON w.user_id = u.user_id;

-- -----------------------------------------------------------------------------
-- 4. Aggregate Functions: SUM, AVG, COUNT, MIN, MAX
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(stock_id) AS total_listed_equities,
    ROUND(AVG(current_price), 2) AS average_stock_price,
    MIN(current_price) AS lowest_price,
    MAX(current_price) AS highest_price,
    SUM(volume) AS total_volume_traded
FROM Stocks;

-- -----------------------------------------------------------------------------
-- 5. GROUP BY and HAVING Clause
-- -----------------------------------------------------------------------------
SELECT 
    sector,
    COUNT(stock_id) AS stocks_count,
    ROUND(AVG(current_price), 2) AS avg_sector_price,
    ROUND(SUM(volume), 0) AS total_sector_volume
FROM Stocks
GROUP BY sector
HAVING COUNT(stock_id) >= 2 AND AVG(current_price) > 1000.00
ORDER BY avg_sector_price DESC;

-- -----------------------------------------------------------------------------
-- 6. Nested Queries and Subqueries (Scalar, IN, EXISTS, Correlated)
-- -----------------------------------------------------------------------------
-- A. Scalar Subquery: Equities priced above market average
SELECT symbol, company_name, current_price
FROM Stocks
WHERE current_price > (SELECT AVG(current_price) FROM Stocks)
ORDER BY current_price DESC;

-- B. IN Subquery: Investors holding IT sector shares
SELECT user_id, name, email
FROM Users
WHERE user_id IN (
    SELECT DISTINCT p.user_id
    FROM Portfolio p
    JOIN Stocks s ON p.stock_id = s.stock_id
    WHERE s.sector = 'Information Tech' AND p.total_quantity > 0
);

-- C. Correlated Subquery with EXISTS: Users having at least one active buy order
SELECT u.user_id, u.name, u.email
FROM Users u
WHERE EXISTS (
    SELECT 1 FROM Transactions t
    WHERE t.user_id = u.user_id AND t.transaction_type = 'BUY'
);

-- -----------------------------------------------------------------------------
-- 7. Querying Relational Views
-- -----------------------------------------------------------------------------
SELECT * FROM vw_portfolio_summary WHERE user_id = 3;
SELECT * FROM vw_user_role_overview;
SELECT * FROM vw_stock_wise_investment ORDER BY total_current_valuation DESC;

-- -----------------------------------------------------------------------------
-- 8. Executing Stored Procedures
-- -----------------------------------------------------------------------------
-- Buy procedure:
CALL sp_buy_stock(3, 8, 2, @status, @msg);
SELECT @status AS buy_status, @msg AS buy_message;

-- Sell procedure:
CALL sp_sell_stock(3, 8, 2, @sell_status, @sell_msg, @pnl);
SELECT @sell_status AS sell_status, @sell_msg AS sell_message, @pnl AS realized_pnl;

-- -----------------------------------------------------------------------------
-- 9. Inspecting Triggers and Audit Log
-- -----------------------------------------------------------------------------
SELECT log_id, acting_user_id, affected_user_id, action, table_name, action_timestamp, description
FROM Audit_Log
ORDER BY log_id DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- 10. ACID Transaction & Rollback Demonstration
-- -----------------------------------------------------------------------------
START TRANSACTION;
UPDATE Users SET cash_balance = cash_balance - 5000.00 WHERE user_id = 3;
-- Rollback intentional test:
ROLLBACK;
SELECT user_id, name, cash_balance FROM Users WHERE user_id = 3;
