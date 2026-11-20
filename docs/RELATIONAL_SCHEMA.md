# Relational Schema Design
## Stock Market Portfolio Management System

This document represents the relational schema mapping with formal table definitions, primary keys (PK), foreign keys (FK), candidate keys (CK), and constraints.

---

### 1. Relational Schema Notation

- **Users** (<ins>user_id</ins>, name, email, phone, password_hash, cash_balance, account_status, created_at, updated_at)
  - **PK**: `user_id`
  - **CK**: `email`
  - **Constraints**: `cash_balance >= 0`, `account_status IN ('ACTIVE', 'SUSPENDED', 'CLOSED')`

- **Stocks** (<ins>stock_id</ins>, symbol, company_name, sector, current_price, day_change, day_change_percent, high_52w, low_52w, volume, updated_at)
  - **PK**: `stock_id`
  - **CK**: `symbol`
  - **Constraints**: `current_price > 0`

- **Transactions** (<ins>transaction_id</ins>, user_id*, stock_id*, transaction_type, quantity, price, total_amount, transaction_date, transaction_time, transaction_status, created_at)
  - **PK**: `transaction_id`
  - **FK**: `user_id` REFERENCES `Users(user_id)` ON DELETE RESTRICT
  - **FK**: `stock_id` REFERENCES `Stocks(stock_id)` ON DELETE RESTRICT
  - **Constraints**: `quantity > 0`, `price > 0`, `total_amount >= 0`, `transaction_type IN ('BUY', 'SELL')`

- **Portfolio** (<ins>portfolio_id</ins>, user_id*, stock_id*, total_quantity, average_buy_price, updated_at)
  - **PK**: `portfolio_id`
  - **CK / Unique**: `(user_id, stock_id)`
  - **FK**: `user_id` REFERENCES `Users(user_id)` ON DELETE CASCADE
  - **FK**: `stock_id` REFERENCES `Stocks(stock_id)` ON DELETE RESTRICT
  - **Constraints**: `total_quantity >= 0`, `average_buy_price >= 0`

- **Watchlist** (<ins>watchlist_id</ins>, user_id*, stock_id*, added_at)
  - **PK**: `watchlist_id`
  - **CK / Unique**: `(user_id, stock_id)`
  - **FK**: `user_id` REFERENCES `Users(user_id)` ON DELETE CASCADE
  - **FK**: `stock_id` REFERENCES `Stocks(stock_id)` ON DELETE CASCADE

- **Admin** (<ins>admin_id</ins>, username, email, password_hash, role, created_at)
  - **PK**: `admin_id`
  - **CK**: `username`, `email`

- **Audit_Log** (<ins>log_id</ins>, user_id*, action, table_name, record_id, action_timestamp, description)
  - **PK**: `log_id`
  - **FK**: `user_id` REFERENCES `Users(user_id)` ON DELETE SET NULL

- **Password_Reset** (<ins>reset_id</ins>, user_id*, reset_token_hash, expiry_time, is_used, created_at)
  - **PK**: `reset_id`
  - **FK**: `user_id` REFERENCES `Users(user_id)` ON DELETE CASCADE

- **Stock_Price_History** (<ins>history_id</ins>, stock_id*, price, recorded_at)
  - **PK**: `history_id`
  - **FK**: `stock_id` REFERENCES `Stocks(stock_id)` ON DELETE CASCADE
  - **Constraints**: `price > 0`

---

### 2. Physical Storage & Indexing Strategy

| Index Name | Table | Columns | Type | Purpose |
|------------|-------|---------|------|---------|
| `PRIMARY` | Users | `user_id` | BTREE | Clustered index on primary key |
| `uq_email` | Users | `email` | BTREE | Enforces unique email constraint |
| `idx_stocks_symbol` | Stocks | `symbol` | BTREE | Rapid lookup on ticker search |
| `idx_stocks_sector` | Stocks | `sector` | BTREE | Fast sector filtering queries |
| `idx_tx_user_date` | Transactions | `user_id, transaction_date` | BTREE | Optimized user transaction reports |
| `uq_user_stock` | Portfolio | `user_id, stock_id` | BTREE | Composite key enforcing single holding row |
| `uq_watchlist` | Watchlist | `user_id, stock_id` | BTREE | Prevents duplicate watchlist entries |
| `idx_hist_stock_date`| Stock_Price_History | `stock_id, recorded_at` | BTREE | Fast retrieval for Chart.js historical charts |
