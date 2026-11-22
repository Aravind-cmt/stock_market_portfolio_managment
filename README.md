# StockPulse

StockPulse is a stock portfolio and simulated paper-trading application implemented with HTML, CSS, JavaScript, Bootstrap 5, PHP 8+, and MySQL 8+.

This PHP version does not use Flask, Python, or SQLite.

## Requirements

- PHP 8.1 or later
- PDO MySQL extension
- MySQL 8.0 or later
- Apache or another PHP-compatible web server
- HTTPS for production

## Installation

1. Import the database files:

```text
database/schema.sql
database/sample_data.sql
database/indexes.sql
database/views.sql
database/procedures.sql
database/triggers.sql
```

2. Copy `.env.example` to the environment configuration used by the hosting provider.

3. Configure:

```text
MYSQL_HOST
MYSQL_PORT
MYSQL_DB
MYSQL_USER
MYSQL_PASSWORD
SESSION_COOKIE_SECURE
```

4. Run the local server:

```powershell
php -S localhost:8000
```

5. Open `http://localhost:8000`.

## Main URLs

### Investor

- `/user/login.php`
- `/user/register.php`
- `/user/forgot-password.php`
- `/user/dashboard.php`
- `/user/market.php`
- `/user/portfolio.php`
- `/user/trade.php`
- `/user/watchlist.php`
- `/user/transactions.php`
- `/reports/index.php`

### Administrator

- `/admin/login.php`
- `/admin/dashboard.php`
- `/admin/users.php`
- `/admin/stocks.php`
- `/admin/transactions.php`

### Super Administrator

- `/admin/admins.php`
- `/admin/add-admin.php`
- `/admin/audit-logs.php`

## Database

The application preserves the existing `Users`, `Roles`, `User_Roles`, `Stocks`, `Transactions`, `Portfolio`, `Watchlist`, `Audit_Log`, `Password_Reset`, and `Stock_Price_History` tables.

It uses MySQL primary keys, foreign keys, unique constraints, CHECK constraints, views, procedures, triggers, InnoDB transactions, and row locking.

## Security

- PDO prepared statements
- PHP password hashing
- CSRF tokens
- Strict PHP sessions
- HttpOnly, SameSite, and optional Secure cookies
- Server-side role checks
- Super Admin-only role management
- Audit logging
- Personal transaction and portfolio filtering
- Environment-variable credentials

## Deployment

Deploy on PHP-compatible hosting with persistent MySQL, for example a VPS or managed PHP hosting service. Configure MySQL environment variables, enable HTTPS, and point the web root at the project directory.
