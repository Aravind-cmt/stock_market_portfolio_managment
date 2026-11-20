import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'stockpulse_secret_key_dbms_2026_super_secure')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'stock_portfolio_db')
    
    # Application Constants
    INITIAL_CASH_BALANCE = 100000.00  # ₹1,00,000 starting paper trading wallet
    ITEMS_PER_PAGE = 15
    
    # Session config
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
