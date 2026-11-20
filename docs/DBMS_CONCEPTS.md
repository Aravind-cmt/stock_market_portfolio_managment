# DBMS Laboratory Implementation Concepts
## Stock Market Portfolio Management System

This document maps the 14 critical DBMS concepts to the concrete architectural implementation in this project.

---

### Concept 1: Primary Keys and Foreign Keys
- **Primary Keys**: Used in every table to uniquely identify records (e.g., `Users.user_id`, `Stocks.stock_id`, `Transactions.transaction_id`).
- **Foreign Keys**: Enforce referential integrity:
  - `Transactions.user_id` $\rightarrow$ `Users.user_id` (`ON DELETE RESTRICT`)
  - `Transactions.stock_id` $\rightarrow$ `Stocks.stock_id` (`ON DELETE RESTRICT`)
  - `Portfolio.user_id` $\rightarrow$ `Users.user_id` (`ON DELETE CASCADE`)

### Concept 2: One-to-Many and Many-to-Many Relationships
- **1 : N (One-to-Many)**: One user executes many transactions; one stock records many historical price entries.
- **M : N (Many-to-Many)**: A user can hold many stocks, and a stock can be held by many users. This is resolved via the junction table `Portfolio` and `Watchlist` with unique composite constraints.

### Concept 3: Database Normalization (1NF, 2NF, 3NF)
- Normalized from an unnormalized trading log to 3NF/BCNF. Eliminates update anomalies, duplicate user records, and partial dependencies.

### Concept 4: SQL JOIN Operations
- **INNER JOIN**: Extracts active holdings by joining `Portfolio`, `Users`, and `Stocks`.
- **LEFT JOIN**: Displays all market stocks including those not currently held in any user's portfolio.
- **RIGHT JOIN**: Evaluates stock-to-watchlist linkages.

### Concept 5: Aggregate Functions (SUM, AVG, COUNT, MIN, MAX)
- Used in `vw_portfolio_summary`, `vw_user_performance`, and report generation to compute `SUM(total_amount)`, `AVG(average_buy_price)`, `COUNT(DISTINCT stock_id)`, `MIN(current_price)`, and `MAX(current_price)`.

### Concept 6: GROUP BY and HAVING Clauses
- Aggregates holdings and transaction history per stock/sector, filtering with `HAVING COUNT(stock_id) >= 2`.

### Concept 7: Nested Queries and Subqueries
- **Scalar Subquery**: Finds stocks trading above market average (`WHERE current_price > (SELECT AVG(current_price) FROM Stocks)`).
- **IN Subquery**: Identifies active traders in specific sectors.
- **EXISTS Subquery**: Correlated lookup for users holding watchlist items.

### Concept 8: Views for Portfolio Summaries
- Four dedicated views:
  1. `vw_portfolio_summary`
  2. `vw_user_performance`
  3. `vw_stock_market_overview`
  4. `vw_daily_transaction_summary`

### Concept 9: Stored Procedures for Buy and Sell Transactions
- `sp_buy_stock`: Handles locking, cash check, balance reduction, weighted average price calculation, portfolio update, and audit logging.
- `sp_sell_stock`: Handles share validation, oversell prevention, revenue calculation, cash credit, portfolio decrement/deletion, and audit logging.
- `sp_update_stock_price`: Administrative procedure to revise prices and trigger history updates.

### Concept 10: Triggers for Auditing and Maintaining Data Integrity
- `trg_after_stock_price_update`: Automatically archives price ticks to `Stock_Price_History`.
- `trg_prevent_negative_cash`: Enforces `cash_balance >= 0` at the database engine level.
- `trg_prevent_negative_portfolio`: Enforces `total_quantity >= 0`.
- `trg_after_user_registration_audit`: Automatically inserts an audit record on new user signups.

### Concept 11: Indexing for Rapid Retrieval
- B-Tree indexes created on `symbol`, `sector`, `user_id`, `stock_id`, `transaction_date`, and `(stock_id, recorded_at)` to eliminate full table scans during searches.

### Concept 12: ACID Properties
- **Atomicity**: In `sp_buy_stock`, cash deduction and portfolio increase either both happen or neither does.
- **Consistency**: All CHECK, NOT NULL, and UNIQUE constraints guarantee valid states.
- **Isolation**: Handled using `SELECT ... FOR UPDATE` row locks, preventing race conditions during concurrent trades.
- **Durability**: InnoDB write-ahead redo logs guarantee committed trades persist across restarts.

### Concept 13: COMMIT and ROLLBACK
- Explicit transactional boundary blocks inside stored procedures and Python service handlers:
  ```sql
  START TRANSACTION;
  -- Operations
  IF error_condition THEN
      ROLLBACK;
  ELSE
      COMMIT;
  END IF;
  ```

### Concept 14: Constraints and Referential Integrity
- `NOT NULL` on mandatory business fields.
- `UNIQUE` on `email`, `symbol`, and `(user_id, stock_id)`.
- `CHECK` constraints on prices, quantities, and balances.
- `FOREIGN KEY ... ON DELETE CASCADE / RESTRICT`.
