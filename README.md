# StockPulse — Stock Market Portfolio Management System
## Full-Stack Web Application + Relational DBMS (MySQL 8.0+)

[![Tech Stack: Python Flask](https://img.shields.io/badge/Backend-Python%20Flask%203.0-blue.svg)](https://flask.palletsprojects.com/)
[![Database: MySQL 8.0+](https://img.shields.io/badge/Database-MySQL%208.0+-orange.svg)](https://www.mysql.com/)
[![Frontend: Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap%205%20%7C%20Chart.js-purple.svg)](https://getbootstrap.com/)
[![DBMS Lab Project](https://img.shields.io/badge/DBMS%20Lab-3rd%20Semester%20Capstone-success.svg)](#)

---

### 1. Executive Summary & Project Objective

**StockPulse** is an institutional-grade Stock Market Portfolio Management and Paper Trading platform designed for the Database Management Systems (DBMS) laboratory. It allows investors to monitor market movements, execute ACID-compliant buy and sell orders, manage investment portfolios with weighted-average cost basis accounting, track profit and loss in real-time, maintain watchlists, and export detailed financial statements.

The system emphasizes core DBMS principles including **relational normalization (1NF, 2NF, 3NF)**, primary and foreign key constraints, composite unique indexes, **InnoDB ACID transactions** with pessimistic row locking (`SELECT ... FOR UPDATE`), pre-compiled **SQL Views**, stored procedures, database **triggers**, and automated audit logging.

---

### 2. Technology Stack

- **Backend**: Python 3.11+, Flask 3.0.3, Jinja2 template engine, Werkzeug security (Scrypt password hashing).
- **Database Engine**: MySQL 8.0+ (InnoDB storage engine), MySQL Workbench, PyMySQL 1.2.4 & `mysql-connector-python`.
  - *Intelligent Fallback*: Includes an automated portable engine mode that runs smoothly on SQLite with identical schema when MySQL Server is not currently active on `localhost:3306`.
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Chart.js 4.4.2.
- **Reporting Engine**: Dynamic CSV streaming export and `@media print` styled financial invoices/statements.

---

### 3. Database Architecture & Schema Design

The relational database (`stock_portfolio_db`) is normalized to **3NF / BCNF** and consists of 9 core tables:

1. **`Users`**: Stores investor credentials, profile information, account status (`ACTIVE`, `SUSPENDED`, `CLOSED`), and simulated paper trading wallet balance (`cash_balance >= 0.00`).
2. **`Stocks`**: Master registry of 22 prominent Indian equities (NSE/BSE) across diverse sectors with current market prices, day changes, 52-week highs/lows, and volume.
3. **`Transactions`**: Immutable audit ledger recording every executed `BUY` and `SELL` order with execution price, quantity, total amount, timestamp, and status.
4. **`Portfolio`**: Junction table resolving the Many-to-Many ($M:N$) relationship between users and stocks. Maintains net shares held and dynamically updated weighted-average purchase price (`average_buy_price`). Enforces composite uniqueness on `(user_id, stock_id)`.
5. **`Watchlist`**: Monitored equities tracked by users with composite uniqueness on `(user_id, stock_id)`.
6. **`Admin`**: Elevated role-based administration accounts for managing stock listings and system surveillance.
7. **`Audit_Log`**: Security compliance log tracking state transitions across tables (`table_name`, `record_id`, `action`, `action_timestamp`, `description`).
8. **`Password_Reset`**: Secure recovery token management with expiration timestamps.
9. **`Stock_Price_History`**: Historical tick data for technical analysis and Chart.js line visualizations.

---

### 4. Implementation of 14 Core DBMS Laboratory Concepts

| No. | Concept | Implementation in StockPulse | Relevant Code / File |
|:---:|:---|:---|:---|
| **1** | **Primary & Foreign Keys** | Every table uses `AUTO_INCREMENT` PKs; FKs enforce referential integrity with `ON DELETE CASCADE` or `RESTRICT`. | `database/schema.sql` |
| **2** | **1:N & M:N Relationships** | 1:N between Users and Transactions; M:N between Users and Stocks resolved through junction tables `Portfolio` and `Watchlist`. | `docs/ER_DIAGRAM.md` |
| **3** | **Database Normalization** | Tables decomposed from unnormalized logs to 1NF (atomic attributes), 2NF (no partial dependencies), and 3NF/BCNF (no transitive dependencies). | `docs/NORMALIZATION.md` |
| **4** | **SQL JOIN Operations** | `INNER JOIN` for active holdings, `LEFT JOIN` for market listings with optional holdings, `RIGHT JOIN` for watchlist evaluations. | `database/dbms_queries.sql` |
| **5** | **Aggregate Functions** | `SUM(total_amount)`, `AVG(average_buy_price)`, `COUNT(stock_id)`, `MIN(current_price)`, `MAX(current_price)`. | `database/views.sql` |
| **6** | **GROUP BY & HAVING** | Grouping market volume by sector with `HAVING COUNT(stock_id) >= 2 AND AVG(current_price) > 1500`. | `database/dbms_queries.sql` |
| **7** | **Nested Queries / Subqueries** | Scalar subqueries for above-average stocks, `IN` subqueries for active traders, correlated `EXISTS` subqueries for watchlists. | `database/dbms_queries.sql` |
| **8** | **SQL Views** | `vw_portfolio_summary`, `vw_user_performance`, `vw_stock_market_overview`, `vw_daily_transaction_summary`. | `database/views.sql` |
| **9** | **Stored Procedures** | `sp_buy_stock` (weighted average price & cash deduction), `sp_sell_stock` (oversell check & realized P&L), `sp_update_stock_price`. | `database/procedures.sql` |
| **10** | **Database Triggers** | `trg_after_stock_price_update` (archives ticks), `trg_prevent_negative_cash`, `trg_prevent_negative_portfolio`, `trg_after_user_registration_audit`. | `database/triggers.sql` |
| **11** | **B-Tree Indexing** | Indexes on `symbol`, `sector`, `user_id`, `stock_id`, `transaction_date`, and `(stock_id, recorded_at)` verified with `EXPLAIN`. | `database/schema.sql` |
| **12** | **ACID Properties** | Atomic execution of wallet balance update + order ledger insertion + portfolio recalculation under InnoDB transactions. | `services/trade_service.py` |
| **13** | **COMMIT & ROLLBACK** | Explicit transactional blocks with rollback on validation failures (e.g., insufficient balance or overselling). | `services/db.py`, `database/procedures.sql` |
| **14** | **Integrity Constraints** | `NOT NULL`, `UNIQUE(email, symbol)`, `CHECK(quantity > 0)`, `CHECK(price > 0)`, `CHECK(cash_balance >= 0)`. | `database/schema.sql` |

---

### 5. Project Directory Structure

```text
stock_portfolio_system/
├── app.py                      # Flask Application entry point and route registration
├── config.py                   # Environment & MySQL connection configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Complete system documentation & lab report
│
├── database/
│   ├── schema.sql              # MySQL DDL (9 tables, constraints, indexes)
│   ├── sample_data.sql         # 10+ Users, 22 Indian stocks, orders, audit logs
│   ├── views.sql               # 4 Relational Views for portfolio & market analytics
│   ├── procedures.sql          # Stored procedures: sp_buy_stock, sp_sell_stock, etc.
│   ├── triggers.sql            # Automated integrity & audit triggers
│   ├── dbms_queries.sql        # Executable queries demonstrating all 14 DBMS concepts
│   └── setup_database.py       # One-click automated database setup script
│
├── docs/
│   ├── ER_DIAGRAM.md           # Entity-Relationship diagram (Mermaid) & cardinalities
│   ├── RELATIONAL_SCHEMA.md    # Formal relational schema notation & primary/foreign keys
│   ├── NORMALIZATION.md        # 1NF, 2NF, 3NF functional dependency proofs & anomalies
│   └── DBMS_CONCEPTS.md        # Detailed mapping of all 14 DBMS lab concepts
│
├── routes/
│   ├── auth.py                 # Registration, login, logout, password recovery
│   ├── dashboard.py            # Investor dashboard & portfolio summary metrics
│   ├── market.py               # Stock market registry & detailed price charts
│   ├── trade.py                # Buy and sell order execution endpoints
│   ├── portfolio.py            # Holdings breakdown & allocation views
│   ├── watchlist.py            # Monitored stock watchlist management
│   ├── transactions.py         # Filterable order audit ledger
│   ├── reports.py              # Financial reports & CSV / Print generation
│   ├── admin.py                # Admin portal: stock CRUD, price updates, user oversight
│   └── api.py                  # JSON REST API for charts, search, and dynamic toggles
│
├── services/
│   ├── db.py                   # Database connection pool, ACID transaction manager
│   ├── market_service.py       # Stock catalog, filtering, and price management
│   ├── trade_service.py        # ACID Buy & Sell trading engine with row locking
│   ├── portfolio_service.py    # Holding calculations, P&L, sector/asset allocation
│   ├── report_service.py       # Financial statement & CSV export generation
│   └── audit_service.py        # System audit trail and admin metrics
│
├── static/
│   ├── css/style.css           # Modern Dark Navy & White theme with print media rules
│   ├── js/main.js              # Quick trade modals, AJAX watchlist toggle, responsive UI
│   └── js/charts.js            # Chart.js sector donut, asset bars, price trend lines
│
└── templates/
    ├── base.html               # Master layout with responsive sidebar and cash pill
    ├── landing.html            # Public landing page with features and demo credentials
    ├── auth/                   # login.html, register.html, forgot_password.html, change_password.html
    ├── dashboard/              # index.html (metrics cards, charts, recent activity)
    ├── market/                 # index.html (catalog), detail.html (charts & order widget)
    ├── trade/                  # buy_sell.html (trade console)
    ├── portfolio/              # index.html (holdings table & visual breakdowns)
    ├── watchlist/              # index.html (monitored equities)
    ├── transactions/           # index.html (historical trade ledger with filters)
    ├── reports/                # index.html (reports hub), printable.html (invoice view)
    └── admin/                  # login.html, index.html, stocks.html, users.html, transactions.html, audit_logs.html
```

---

### 6. Pre-Configured Demo Accounts

The database comes pre-seeded with realistic demonstration accounts:

| Role | Email | Password | Initial Paper Cash | Purpose |
|:---|:---|:---|:---|:---|
| **Investor** | `aravind@gmail.com` | `Password@123` | ₹1,45,200.00 | Active portfolio with RELIANCE, INFY, HDFCBANK holdings |
| **Investor** | `priya.nair@outlook.com` | `Password@123` | ₹82,500.00 | Active portfolio with TCS, ICICIBANK, ITC holdings |
| **Investor** | `rahul.verma@gmail.com` | `Password@123` | ₹94,000.00 | Holdings in SBIN, TATAMOTORS, NTPC |
| **New User** | *(Register via UI)* | *(Custom)* | ₹1,00,000.00 | Instant signup with ₹1 Lakh welcome cash |
| **Administrator** | `admin@stockpulse.com` | `Admin@123` | N/A | Full stock CRUD, price updates, user & audit logs |

---

### 7. Step-by-Step Installation & Execution Instructions

#### Prerequisites
1. **Python 3.10+** installed on Windows.
2. **MySQL Server 8.0+** & **MySQL Workbench** installed (or use the built-in automatic fallback engine).

---

#### Option A: Running with Live MySQL 8.0+

1. **Start MySQL Server**:
   Ensure the MySQL 8.0 service is running on `localhost:3306`.

2. **Configure Database Credentials**:
   Edit `config.py` (or set environment variables):
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_PORT = 3306
   MYSQL_USER = 'root'
   MYSQL_PASSWORD = 'your_mysql_password'
   MYSQL_DB = 'stock_portfolio_db'
   ```

3. **Import SQL via MySQL Workbench**:
   - Open MySQL Workbench and connect to your local MySQL instance.
   - Open and execute `database/schema.sql` to create database and tables.
   - Open and execute `database/sample_data.sql` to load users, stocks, and trades.
   - Open and execute `database/views.sql` to create views.
   - Open and execute `database/procedures.sql` to register stored procedures.
   - Open and execute `database/triggers.sql` to register triggers.

   *Alternatively, run the automated Python loader:*
   ```powershell
   python database/setup_database.py
   ```

4. **Install Python Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Start the Flask Web Server**:
   ```powershell
   python app.py
   ```

6. **Open in Browser**:
   Navigate to **`http://localhost:5000`** in your browser.

---

#### Option B: Instant Offline / Lab Demo Mode

If MySQL Server is not currently running on port 3306, **StockPulse automatically activates its built-in dual-engine fallback**, creating an identical schema database (`portfolio_dev.db`) loaded with all 10 users, 22 Indian stocks, order histories, and audit records.

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Initialize Database**:
   ```powershell
   python database/setup_database.py
   ```

3. **Start Application**:
   ```powershell
   python app.py
   ```

4. **Access the Website**:
   Visit **`http://localhost:5000`**.

---

### 8. Verification & Testing Workflow

1. **Public Landing Page**:
   - Open `http://localhost:5000/`. Review the feature breakdown, technology stack, and demo accounts.
2. **User Registration & Instant Paper Cash**:
   - Navigate to `/register`. Register a new account.
   - Verify that ₹1,00,000 is credited automatically to your paper wallet.
3. **User Login & Dashboard**:
   - Log in with `aravind@gmail.com` / `Password@123`.
   - Inspect the summary cards (Portfolio Value, Capital Invested, Overall P&L, Cash Wallet).
   - Review the Chart.js Sector Donut Chart and Holdings Valuation Bar Chart.
4. **Browsing Indian Equities**:
   - Navigate to `/market`.
   - Filter by Sector (e.g., *Banking & Finance*, *Information Tech*, *Automobile*).
   - Use the live search box to find specific tickers (e.g., `RELIANCE`, `TCS`, `INFY`).
5. **Executing a BUY Order**:
   - Click **Buy** on any stock (e.g., `TATAMOTORS` or `ITC`).
   - Enter quantity (e.g., 5 shares). Confirm order.
   - Observe that cash balance is deducted, holdings are created/updated with weighted-average cost, and an entry is logged in `Transactions` and `Audit_Log`.
6. **Executing a SELL Order & Oversell Prevention**:
   - Click **Sell** on an owned stock.
   - Attempt to sell more shares than owned (e.g., 999 shares) $\rightarrow$ verify that the backend rejects the transaction with a protective error message.
   - Sell a valid number of shares $\rightarrow$ verify cash credit and realized P&L calculation.
7. **Watchlist Operations**:
   - Click the star icon on any stock card to add/remove from your Watchlist via AJAX.
8. **Reports & CSV / Print Export**:
   - Navigate to `/reports`.
   - Switch between *All Transactions*, *Buy Orders*, *Sell Orders*, *Portfolio Holdings*, and *Profit & Loss*.
   - Click **Download CSV** to receive an instant `.csv` file.
   - Click **Print Report** to open a clean, formatted statement view ready for PDF saving or printing.
9. **Admin Portal**:
   - Log in at `/admin/login` using `admin@stockpulse.com` / `Admin@123`.
   - View system metrics, manage registered users, add new stock listings, update market prices, view all transactions, and inspect the real-time `Audit_Log`.

---

### 9. Academic Project Disclaimer

This project is developed for educational purposes as part of the Database Management Systems (DBMS) laboratory curriculum. Stock prices and quotes are demonstration data and do not reflect real-time live market exchanges. All trading transactions are simulated paper trades executed within the application's relational database.
