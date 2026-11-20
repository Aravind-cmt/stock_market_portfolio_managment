import os
import sqlite3
import pymysql
import pymysql.cursors
from datetime import datetime, date
from decimal import Decimal
from config import Config

_engine_mode = None  # 'mysql' or 'sqlite'
_sqlite_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'portfolio_dev.db')

def get_db_mode():
    global _engine_mode
    if _engine_mode is not None:
        return _engine_mode
    
    # Try connecting to MySQL
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            connect_timeout=2
        )
        conn.close()
        _engine_mode = 'mysql'
        print("[DB] Connected to MySQL Server at {}:{}".format(Config.MYSQL_HOST, Config.MYSQL_PORT))
    except Exception as e:
        _engine_mode = 'sqlite'
        print(f"[DB] Notice: MySQL Server not reachable ({e}). Running in SQLite fallback mode with identical schema.")
    return _engine_mode

def get_connection():
    mode = get_db_mode()
    if mode == 'mysql':
        try:
            return pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )
        except pymysql.err.OperationalError as e:
            # If database doesn't exist, connect without database to create it
            if e.args[0] in (1049,):
                root_conn = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    autocommit=True
                )
                with root_conn.cursor() as cur:
                    cur.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4;")
                root_conn.close()
                return pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False,
                    charset='utf8mb4'
                )
            raise e
    else:
        # SQLite connection
        conn = sqlite3.connect(_sqlite_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign key support in SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

def execute_query(query, params=None, fetch='all'):
    """
    Executes a SELECT query with parameterized inputs to prevent SQL injection.
    Automatically handles placeholder differences between MySQL (%s) and SQLite (? or %s).
    """
    mode = get_db_mode()
    conn = get_connection()
    try:
        if mode == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch == 'all':
                    res = cursor.fetchall()
                elif fetch == 'one':
                    res = cursor.fetchone()
                else:
                    res = None
                return res
        else:
            # Adapt query placeholder from %s to ? for SQLite
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, params or ())
            if fetch == 'all':
                rows = cursor.fetchall()
                res = [dict(row) for row in rows]
            elif fetch == 'one':
                row = cursor.fetchone()
                res = dict(row) if row else None
            else:
                res = None
            cursor.close()
            return res
    finally:
        conn.close()

def execute_update(query, params=None, commit=True):
    """
    Executes an INSERT, UPDATE, or DELETE statement with parameterization.
    Returns lastrowid.
    """
    mode = get_db_mode()
    conn = get_connection()
    try:
        if mode == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                last_id = cursor.lastrowid
            if commit:
                conn.commit()
            return last_id
        else:
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, params or ())
            last_id = cursor.lastrowid
            if commit:
                conn.commit()
            cursor.close()
            return last_id
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()

class TransactionScope:
    """
    Context manager implementing ACID transaction boundaries:
    START TRANSACTION / BEGIN, with automatic COMMIT on success and ROLLBACK on exception.
    """
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.mode = get_db_mode()

    def __enter__(self):
        self.conn = get_connection()
        if self.mode == 'mysql':
            self.cursor = self.conn.cursor()
            self.cursor.execute("START TRANSACTION;")
        else:
            self.cursor = self.conn.cursor()
            self.cursor.execute("BEGIN TRANSACTION;")
        return self

    def execute(self, query, params=None):
        if self.mode == 'mysql':
            self.cursor.execute(query, params or ())
            return self.cursor
        else:
            sqlite_query = query.replace('%s', '?')
            # Strip FOR UPDATE if present in SQLite
            sqlite_query = sqlite_query.replace('FOR UPDATE', '')
            self.cursor.execute(sqlite_query, params or ())
            return self.cursor

    def fetchone(self):
        if self.mode == 'mysql':
            return self.cursor.fetchone()
        else:
            row = self.cursor.fetchone()
            return dict(row) if row else None

    def fetchall(self):
        if self.mode == 'mysql':
            return self.cursor.fetchall()
        else:
            rows = self.cursor.fetchall()
            return [dict(r) for r in rows]

    def lastrowid(self):
        return self.cursor.lastrowid

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.conn.rollback()
                print(f"[ACID Transaction] Rolled back due to error: {exc_val}")
            else:
                self.conn.commit()
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        return False
