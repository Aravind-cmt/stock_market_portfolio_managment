-- =============================================================================
-- Stock Market Portfolio Management System
-- SQL Views Definition (MySQL 8.0+)
-- =============================================================================

USE stock_portfolio_db;

DROP VIEW IF EXISTS vw_daily_transaction_summary;
DROP VIEW IF EXISTS vw_stock_market_overview;
DROP VIEW IF EXISTS vw_user_performance;
DROP VIEW IF EXISTS vw_portfolio_summary;

-- -----------------------------------------------------------------------------
-- 1. View: vw_portfolio_summary
-- Joins Portfolio with Users and Stocks to compute holding value, total
-- invested capital, unrealized profit/loss, and return percentage.
-- -----------------------------------------------------------------------------
CREATE VIEW vw_portfolio_summary AS
SELECT 
    p.portfolio_id,
    p.user_id,
    u.name AS user_name,
    u.email AS user_email,
    p.stock_id,
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
    p.updated_at AS last_updated
FROM Portfolio p
JOIN Users u ON p.user_id = u.user_id
JOIN Stocks s ON p.stock_id = s.stock_id
WHERE p.total_quantity > 0;

-- -----------------------------------------------------------------------------
-- 2. View: vw_user_performance
-- Aggregates all holdings per user to compute total investment, total current
-- portfolio value, total unrealized profit/loss, cash wallet, and net worth.
-- -----------------------------------------------------------------------------
CREATE VIEW vw_user_performance AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    u.cash_balance,
    u.account_status,
    COUNT(p.portfolio_id) AS distinct_stocks_owned,
    COALESCE(SUM(p.total_quantity), 0) AS total_shares_held,
    COALESCE(SUM(ROUND(p.total_quantity * p.average_buy_price, 2)), 0.00) AS total_invested,
    COALESCE(SUM(ROUND(p.total_quantity * s.current_price, 2)), 0.00) AS total_portfolio_value,
    COALESCE(SUM(ROUND((p.total_quantity * s.current_price) - (p.total_quantity * p.average_buy_price), 2)), 0.00) AS total_unrealized_profit_loss,
    ROUND(
        CASE 
            WHEN SUM(p.total_quantity * p.average_buy_price) > 0 THEN
                ((SUM(p.total_quantity * s.current_price) - SUM(p.total_quantity * p.average_buy_price)) / SUM(p.total_quantity * p.average_buy_price)) * 100
            ELSE 0.00 
        END, 2
    ) AS overall_return_percent,
    ROUND(u.cash_balance + COALESCE(SUM(p.total_quantity * s.current_price), 0.00), 2) AS total_net_worth
FROM Users u
LEFT JOIN Portfolio p ON u.user_id = p.user_id AND p.total_quantity > 0
LEFT JOIN Stocks s ON p.stock_id = s.stock_id
GROUP BY u.user_id, u.name, u.email, u.cash_balance, u.account_status;

-- -----------------------------------------------------------------------------
-- 3. View: vw_stock_market_overview
-- Gives comprehensive stock statistics with ownership frequency and total holders.
-- -----------------------------------------------------------------------------
CREATE VIEW vw_stock_market_overview AS
SELECT 
    s.stock_id,
    s.symbol,
    s.company_name,
    s.sector,
    s.current_price,
    s.day_change,
    s.day_change_percent,
    s.high_52w,
    s.low_52w,
    s.volume,
    s.updated_at,
    COUNT(DISTINCT p.user_id) AS total_investors,
    COALESCE(SUM(p.total_quantity), 0) AS total_shares_in_circulation,
    COUNT(DISTINCT w.user_id) AS watchlist_count
FROM Stocks s
LEFT JOIN Portfolio p ON s.stock_id = p.stock_id AND p.total_quantity > 0
LEFT JOIN Watchlist w ON s.stock_id = w.stock_id
GROUP BY s.stock_id, s.symbol, s.company_name, s.sector, s.current_price, 
         s.day_change, s.day_change_percent, s.high_52w, s.low_52w, s.volume, s.updated_at;

-- -----------------------------------------------------------------------------
-- 4. View: vw_daily_transaction_summary
-- Aggregates daily trading activity grouped by date and transaction type.
-- -----------------------------------------------------------------------------
CREATE VIEW vw_daily_transaction_summary AS
SELECT 
    t.transaction_date,
    t.transaction_type,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(t.quantity) AS total_volume_traded,
    ROUND(SUM(t.total_amount), 2) AS total_turnover,
    ROUND(AVG(t.price), 2) AS average_execution_price
FROM Transactions t
WHERE t.transaction_status = 'COMPLETED'
GROUP BY t.transaction_date, t.transaction_type
ORDER BY t.transaction_date DESC, t.transaction_type;
