-- =============================================================================
-- Stock Market Portfolio Management System
-- Performance Index Definitions (MySQL 8.0+)
-- =============================================================================

USE stock_portfolio_db;

-- -----------------------------------------------------------------------------
-- Indexes on Stocks Table
-- Facilitates high-speed lookups by ticker symbol, sector filtering, and price sorting
-- -----------------------------------------------------------------------------
CREATE INDEX idx_stocks_symbol ON Stocks(symbol);
CREATE INDEX idx_stocks_sector ON Stocks(sector);
CREATE INDEX idx_stocks_price ON Stocks(current_price);

-- -----------------------------------------------------------------------------
-- Indexes on Transactions Table
-- Optimizes historical report generation, investor statement retrieval, and date filtering
-- -----------------------------------------------------------------------------
CREATE INDEX idx_transactions_user ON Transactions(user_id);
CREATE INDEX idx_transactions_stock ON Transactions(stock_id);
CREATE INDEX idx_transactions_date ON Transactions(transaction_date);
CREATE INDEX idx_transactions_user_date ON Transactions(user_id, transaction_date);
CREATE INDEX idx_transactions_type ON Transactions(transaction_type);

-- -----------------------------------------------------------------------------
-- Indexes on Portfolio & Watchlist
-- Ensures instantaneous holding evaluation and watchlist retrieval
-- -----------------------------------------------------------------------------
CREATE INDEX idx_portfolio_user ON Portfolio(user_id);
CREATE INDEX idx_watchlist_user ON Watchlist(user_id);

-- -----------------------------------------------------------------------------
-- Indexes on Audit_Log Table
-- Supports rapid filtering by acting user and reverse chronological audit streams
-- -----------------------------------------------------------------------------
CREATE INDEX idx_audit_acting_user ON Audit_Log(acting_user_id);
CREATE INDEX idx_audit_timestamp ON Audit_Log(action_timestamp);

-- -----------------------------------------------------------------------------
-- Indexes on Stock_Price_History Table
-- Composite B-Tree index for sequential chronological trend charts
-- -----------------------------------------------------------------------------
CREATE INDEX idx_price_history_stock_date ON Stock_Price_History(stock_id, recorded_at);
