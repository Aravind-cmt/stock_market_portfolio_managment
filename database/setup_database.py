import os
import sys
import pymysql

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from services.db import get_db_mode, execute_update, execute_query, _sqlite_path

def split_sql_statements(content):
    """
    Splits SQL script honoring DELIMITER $$ and standard semicolons.
    """
    statements = []
    current_delimiter = ';'
    buffer = []
    
    for line in content.splitlines():
        trimmed = line.strip()
        if trimmed.startswith('--') or not trimmed:
            continue
        if trimmed.upper().startswith('DELIMITER'):
            parts = trimmed.split()
            if len(parts) > 1:
                current_delimiter = parts[1]
            continue
        
        buffer.append(line)
        if current_delimiter == ';' and trimmed.endswith(';'):
            statements.append('\n'.join(buffer)[:-1].strip())
            buffer = []
        elif current_delimiter != ';' and trimmed.endswith(current_delimiter):
            stmt = '\n'.join(buffer)
            stmt = stmt[: -len(current_delimiter)].strip()
            statements.append(stmt)
            buffer = []
            
    if buffer:
        remaining = '\n'.join(buffer).strip()
        if remaining:
            statements.append(remaining)
    return [s for s in statements if s]

def setup_mysql():
    print(f"Connecting to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        autocommit=True
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4;")
    cursor.execute(f"USE {Config.MYSQL_DB};")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_files = [
        'schema.sql',
        'sample_data.sql',
        'views.sql',
        'procedures.sql',
        'triggers.sql'
    ]
    
    for filename in sql_files:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            print(f"Executing {filename} on MySQL...")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            statements = split_sql_statements(content)
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    print(f"  [Warning in {filename}]: {e} on statement:\n{stmt[:80]}...")
        else:
            print(f"File {filename} not found.")
            
    cursor.close()
    conn.close()
    print("MySQL database setup completed successfully!")

def setup_sqlite():
    import sqlite3
    print(f"Initializing SQLite fallback database at {_sqlite_path}...")
    conn = sqlite3.connect(_sqlite_path)
    cur = conn.cursor()
    
    # Enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables
    cur.executescript("""
    DROP TABLE IF EXISTS Stock_Price_History;
    DROP TABLE IF EXISTS Password_Reset;
    DROP TABLE IF EXISTS Audit_Log;
    DROP TABLE IF EXISTS Watchlist;
    DROP TABLE IF EXISTS Portfolio;
    DROP TABLE IF EXISTS Transactions;
    DROP TABLE IF EXISTS Stocks;
    DROP TABLE IF EXISTS Admin;
    DROP TABLE IF EXISTS Users;

    CREATE TABLE Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        cash_balance REAL NOT NULL DEFAULT 100000.00,
        account_status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CHECK (cash_balance >= 0.00)
    );

    CREATE TABLE Stocks (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        company_name TEXT NOT NULL,
        sector TEXT NOT NULL,
        current_price REAL NOT NULL,
        day_change REAL NOT NULL DEFAULT 0.00,
        day_change_percent REAL NOT NULL DEFAULT 0.00,
        high_52w REAL,
        low_52w REAL,
        volume INTEGER NOT NULL DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CHECK (current_price > 0.00)
    );

    CREATE TABLE Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        total_amount REAL NOT NULL,
        transaction_date TEXT NOT NULL,
        transaction_time TEXT NOT NULL,
        transaction_status TEXT NOT NULL DEFAULT 'COMPLETED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT,
        FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE RESTRICT,
        CHECK (quantity > 0),
        CHECK (price > 0.00),
        CHECK (total_amount >= 0.00)
    );

    CREATE TABLE Portfolio (
        portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_id INTEGER NOT NULL,
        total_quantity INTEGER NOT NULL DEFAULT 0,
        average_buy_price REAL NOT NULL DEFAULT 0.00,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, stock_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE RESTRICT,
        CHECK (total_quantity >= 0),
        CHECK (average_buy_price >= 0.00)
    );

    CREATE TABLE Watchlist (
        watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        stock_id INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (user_id, stock_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE
    );

    CREATE TABLE Admin (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'SUPER_ADMIN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE Audit_Log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NULL,
        action TEXT NOT NULL,
        table_name TEXT NOT NULL,
        record_id INTEGER NULL,
        action_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
    );

    CREATE TABLE Password_Reset (
        reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reset_token_hash TEXT NOT NULL,
        expiry_time TIMESTAMP NOT NULL,
        is_used INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );

    CREATE TABLE Stock_Price_History (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        price REAL NOT NULL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stock_id) REFERENCES Stocks(stock_id) ON DELETE CASCADE,
        CHECK (price > 0.00)
    );

    CREATE INDEX idx_stocks_symbol ON Stocks(symbol);
    CREATE INDEX idx_stocks_sector ON Stocks(sector);
    CREATE INDEX idx_transactions_user ON Transactions(user_id);
    CREATE INDEX idx_transactions_date ON Transactions(transaction_date);
    CREATE INDEX idx_portfolio_user ON Portfolio(user_id);
    CREATE INDEX idx_watchlist_user ON Watchlist(user_id);
    CREATE INDEX idx_price_history_stock ON Stock_Price_History(stock_id, recorded_at);
    """)

    # Populate Sample Data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_data_path = os.path.join(base_dir, 'sample_data.sql')
    if os.path.exists(sample_data_path):
        with open(sample_data_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        clean_lines = []
        for line in lines:
            if line.strip().upper().startswith('USE '):
                continue
            clean_lines.append(line)
        sql_content = ''.join(clean_lines)
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        for stmt in statements:
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"  [SQLite Insert Notice]: {e}")
                
    conn.commit()
    conn.close()
    print("SQLite fallback database initialized with sample data successfully!")

def init_db():
    mode = get_db_mode()
    if mode == 'mysql':
        try:
            setup_mysql()
        except Exception as e:
            print(f"[Notice] Could not initialize MySQL ({e}). Setting up SQLite fallback...")
            setup_sqlite()
    else:
        setup_sqlite()

if __name__ == '__main__':
    init_db()
