-- =============================================================================
-- Stock Market Portfolio Management System
-- Demonstration Queries for 14 Core DBMS Concepts (MySQL 8.0+)
-- =============================================================================

USE stock_portfolio_db;

-- -----------------------------------------------------------------------------
-- CONCEPT 1: Primary Keys and Foreign Keys
-- Demonstrates referential integrity: Every transaction links uniquely to a
-- parent User (user_id) and Stock (stock_id).
-- -----------------------------------------------------------------------------
SELECT 
    t.transaction_id,
    u.user_id,
    u.name AS investor_name,
    s.stock_id,
    s.symbol AS stock_ticker,
    t.transaction_type,
    t.quantity,
    t.price,
    t.total_amount
FROM Transactions t
JOIN Users u ON t.user_id = u.user_id      -- FK: t.user_id -> u.user_id (PK)
JOIN Stocks s ON t.stock_id = s.stock_id   -- FK: t.stock_id -> s.stock_id (PK)
ORDER BY t.transaction_id;

-- -----------------------------------------------------------------------------
-- CONCEPT 2: One-to-Many and Many-to-Many Relationships
-- 1-to-Many: 1 User has Many Transactions.
-- Many-to-Many: Users and Stocks have a M:N relationship resolved via the
-- junction table `Portfolio` and `Watchlist`.
-- -----------------------------------------------------------------------------
-- Query showing M:N relationship resolved via junction table Portfolio:
SELECT 
    u.name AS investor,
    GROUP_CONCAT(DISTINCT s.symbol ORDER BY s.symbol SEPARATOR ', ') AS portfolio_holdings,
    COUNT(p.stock_id) AS total_stocks_held
FROM Users u
JOIN Portfolio p ON u.user_id = p.user_id
JOIN Stocks s ON p.stock_id = s.stock_id
GROUP BY u.user_id, u.name;

-- -----------------------------------------------------------------------------
-- CONCEPT 3: Database Normalization (1NF, 2NF, 3NF Proof Query)
-- Verifies no repeating groups (1NF), no partial dependencies on composite keys
-- (2NF in Portfolio), and no transitive dependencies (3NF).
-- -----------------------------------------------------------------------------
SELECT 
    p.user_id,
    p.stock_id,
    p.total_quantity,
    p.average_buy_price,
    s.company_name,
    s.sector
FROM Portfolio p
JOIN Stocks s ON p.stock_id = s.stock_id
WHERE p.user_id = 1;

-- -----------------------------------------------------------------------------
-- CONCEPT 4: SQL JOIN Operations (INNER, LEFT, RIGHT, FULL OUTER simulation)
-- -----------------------------------------------------------------------------
-- A. INNER JOIN: Only users who actively hold stocks
SELECT u.name, s.symbol, p.total_quantity, p.average_buy_price
FROM Users u
INNER JOIN Portfolio p ON u.user_id = p.user_id
INNER JOIN Stocks s ON p.stock_id = s.stock_id;

-- B. LEFT JOIN: All stocks, including those not currently in any user's portfolio
SELECT s.symbol, s.company_name, COALESCE(SUM(p.total_quantity), 0) AS market_shares_held
FROM Stocks s
LEFT JOIN Portfolio p ON s.stock_id = p.stock_id
GROUP BY s.stock_id, s.symbol, s.company_name
ORDER BY market_shares_held DESC;

-- C. RIGHT JOIN: Watchlist entries joined with stocks
SELECT w.watchlist_id, u.name, s.symbol, s.current_price
FROM Watchlist w
RIGHT JOIN Stocks s ON w.stock_id = s.stock_id
LEFT JOIN Users u ON w.user_id = u.user_id;

-- -----------------------------------------------------------------------------
-- CONCEPT 5: Aggregate Functions (SUM, AVG, COUNT, MIN, MAX)
-- Computes key market and portfolio metrics.
-- -----------------------------------------------------------------------------
SELECT 
    COUNT(stock_id) AS total_listed_stocks,
    ROUND(AVG(current_price), 2) AS average_stock_price,
    MIN(current_price) AS lowest_price_stock,
    MAX(current_price) AS highest_price_stock,
    SUM(volume) AS total_market_volume
FROM Stocks;

-- -----------------------------------------------------------------------------
-- CONCEPT 6: GROUP BY and HAVING Clause
-- Finds sectors having an average stock price exceeding ₹1,500 with more than 1 stock.
-- -----------------------------------------------------------------------------
SELECT 
    sector,
    COUNT(stock_id) AS stock_count,
    ROUND(AVG(current_price), 2) AS avg_sector_price,
    MIN(current_price) AS min_sector_price,
    MAX(current_price) AS max_sector_price
FROM Stocks
GROUP BY sector
HAVING COUNT(stock_id) >= 2 AND AVG(current_price) > 1500.00
ORDER BY avg_sector_price DESC;

-- -----------------------------------------------------------------------------
-- CONCEPT 7: Nested Queries and Subqueries (Scalar, IN, Correlated, EXISTS)
-- -----------------------------------------------------------------------------
-- A. Scalar Subquery: Stocks priced higher than the overall market average
SELECT symbol, company_name, current_price
FROM Stocks
WHERE current_price > (SELECT AVG(current_price) FROM Stocks)
ORDER BY current_price DESC;

-- B. IN Subquery: Users who have traded IT sector stocks
SELECT DISTINCT u.user_id, u.name, u.email
FROM Users u
WHERE u.user_id IN (
    SELECT t.user_id 
    FROM Transactions t
    JOIN Stocks s ON t.stock_id = s.stock_id
    WHERE s.sector = 'Information Tech'
);

-- C. Correlated Subquery with EXISTS: Users who have at least one stock in Watchlist
SELECT u.user_id, u.name, u.email
FROM Users u
WHERE EXISTS (
    SELECT 1 FROM Watchlist w WHERE w.user_id = u.user_id
);

-- -----------------------------------------------------------------------------
-- CONCEPT 8: Views for Portfolio Summaries
-- Querying pre-compiled relational views.
-- -----------------------------------------------------------------------------
SELECT * FROM vw_portfolio_summary WHERE user_id = 1;
SELECT * FROM vw_user_performance ORDER BY total_net_worth DESC;

-- -----------------------------------------------------------------------------
-- CONCEPT 9: Stored Procedures Execution
-- Demonstrates calling sp_buy_stock and sp_sell_stock.
-- -----------------------------------------------------------------------------
-- Call buy procedure: User 1 buys 2 shares of ITC (stock_id = 8)
CALL sp_buy_stock(1, 8, 2, @status, @message);
SELECT @status AS buy_status, @message AS buy_message;

-- Call sell procedure: User 1 sells 2 shares of ITC (stock_id = 8)
CALL sp_sell_stock(1, 8, 2, @sell_status, @sell_message, @pnl);
SELECT @sell_status AS sell_status, @sell_message AS sell_message, @pnl AS realized_pnl;

-- -----------------------------------------------------------------------------
-- CONCEPT 10: Triggers for Auditing and Integrity
-- Inspecting automatic audit logs created by triggers and procedures.
-- -----------------------------------------------------------------------------
SELECT log_id, user_id, action, table_name, action_timestamp, description
FROM Audit_Log
ORDER BY log_id DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- CONCEPT 11: Indexing and Query Optimization
-- Using EXPLAIN to demonstrate indexed lookups versus table scans.
-- -----------------------------------------------------------------------------
EXPLAIN SELECT * FROM Stocks WHERE symbol = 'RELIANCE';
EXPLAIN SELECT * FROM Transactions WHERE user_id = 1 AND transaction_date >= '2026-01-01';

-- -----------------------------------------------------------------------------
-- CONCEPT 12 & 13: ACID Properties, COMMIT and ROLLBACK
-- Demonstrates an atomic transaction: Either both steps succeed or neither does.
-- -----------------------------------------------------------------------------
START TRANSACTION;

-- Step 1: Deduct ₹5000 from user 1
UPDATE Users SET cash_balance = cash_balance - 5000.00 WHERE user_id = 1;

-- Step 2: Intentionally trigger test rollback to demonstrate Atomicity
-- In case of failure:
ROLLBACK;
-- If successful:
-- COMMIT;

-- Verify user balance remained unchanged after rollback:
SELECT user_id, name, cash_balance FROM Users WHERE user_id = 1;

-- -----------------------------------------------------------------------------
-- CONCEPT 14: Constraints and Referential Integrity
-- Demonstrating CHECK constraint, UNIQUE constraint, and Foreign Key constraints.
-- -----------------------------------------------------------------------------
-- A. Attempting to insert negative cash balance (Fails due to chk_cash_balance)
-- INSERT INTO Users (name, email, phone, password_hash, cash_balance)
-- VALUES ('Fail Test', 'fail@test.com', '1234567890', 'hash', -500.00);

-- B. Attempting duplicate watchlist entry (Fails due to uq_watchlist_user_stock)
-- INSERT INTO Watchlist (user_id, stock_id) VALUES (1, 2); -- (Already exists)

-- C. Checking active table constraints:
SELECT 
    table_name, 
    constraint_name, 
    constraint_type 
FROM information_schema.table_constraints
WHERE table_schema = 'stock_portfolio_db';
