from services.db import execute_query, execute_update, TransactionScope, get_db_mode
from datetime import datetime

def get_all_stocks(search=None, sector=None):
    query = "SELECT * FROM Stocks WHERE 1=1"
    params = []
    if search:
        query += " AND (symbol LIKE %s OR company_name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if sector and sector != 'ALL':
        query += " AND sector = %s"
        params.append(sector)
    query += " ORDER BY symbol ASC"
    return execute_query(query, params, fetch='all')

def get_stock_by_id(stock_id):
    query = "SELECT * FROM Stocks WHERE stock_id = %s"
    return execute_query(query, (stock_id,), fetch='one')

def get_stock_by_symbol(symbol):
    query = "SELECT * FROM Stocks WHERE symbol = %s"
    return execute_query(query, (symbol,), fetch='one')

def get_sectors():
    query = "SELECT DISTINCT sector FROM Stocks ORDER BY sector ASC"
    rows = execute_query(query, fetch='all')
    return [r['sector'] for r in rows if r['sector']]

def get_stock_price_history(stock_id, limit=15):
    query = """
    SELECT price, recorded_at 
    FROM Stock_Price_History 
    WHERE stock_id = %s 
    ORDER BY recorded_at ASC
    """
    rows = execute_query(query, (stock_id,), fetch='all')
    return rows[-limit:] if rows else []

def get_market_summary():
    stocks = execute_query("SELECT * FROM Stocks ORDER BY day_change_percent DESC", fetch='all')
    total_volume = sum(s.get('volume', 0) for s in stocks)
    gainers = [s for s in stocks if s.get('day_change_percent', 0) > 0][:5]
    losers = [s for s in reversed(stocks) if s.get('day_change_percent', 0) < 0][:5]
    return {
        'total_stocks': len(stocks),
        'total_volume': total_volume,
        'gainers': gainers,
        'losers': losers
    }

def add_stock(symbol, company_name, sector, current_price, high_52w=None, low_52w=None):
    symbol = symbol.strip().upper()
    current_price = float(current_price)
    high_52w = float(high_52w) if high_52w else current_price * 1.15
    low_52w = float(low_52w) if low_52w else current_price * 0.85
    
    with TransactionScope() as tx:
        query = """
        INSERT INTO Stocks (symbol, company_name, sector, current_price, high_52w, low_52w, day_change, day_change_percent, volume)
        VALUES (%s, %s, %s, %s, %s, %s, 0.00, 0.00, 100000)
        """
        tx.execute(query, (symbol, company_name, sector, current_price, high_52w, low_52w))
        stock_id = tx.lastrowid()
        
        # Insert initial price history
        tx.execute(
            "INSERT INTO Stock_Price_History (stock_id, price) VALUES (%s, %s)",
            (stock_id, current_price)
        )
        # Log to audit
        tx.execute(
            "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
            (None, 'ADD_STOCK', 'Stocks', stock_id, f"Added new stock {symbol} at ₹{current_price}")
        )
        return stock_id

def update_stock(stock_id, company_name, sector, high_52w, low_52w):
    query = """
    UPDATE Stocks 
    SET company_name = %s, sector = %s, high_52w = %s, low_52w = %s, updated_at = CURRENT_TIMESTAMP
    WHERE stock_id = %s
    """
    execute_update(query, (company_name, sector, high_52w, low_52w, stock_id))
    execute_update(
        "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
        (None, 'UPDATE_STOCK', 'Stocks', stock_id, f"Updated stock info for stock_id {stock_id}")
    )

def update_stock_price(stock_id, new_price):
    new_price = float(new_price)
    with TransactionScope() as tx:
        stock = tx.execute("SELECT * FROM Stocks WHERE stock_id = %s", (stock_id,)).fetchone()
        if not stock:
            raise ValueError("Stock not found.")
        old_price = float(stock['current_price'])
        change = round(new_price - old_price, 2)
        change_pct = round((change / old_price) * 100, 2) if old_price > 0 else 0.0
        
        tx.execute("""
            UPDATE Stocks 
            SET current_price = %s, day_change = %s, day_change_percent = %s, updated_at = CURRENT_TIMESTAMP
            WHERE stock_id = %s
        """, (new_price, change, change_pct, stock_id))
        
        tx.execute("INSERT INTO Stock_Price_History (stock_id, price) VALUES (%s, %s)", (stock_id, new_price))
        
        tx.execute(
            "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
            (None, 'PRICE_UPDATE', 'Stocks', stock_id, f"Price updated from ₹{old_price} to ₹{new_price} ({change_pct}%)")
        )

def delete_stock(stock_id):
    # Ensure stock is not in any active portfolio
    holdings = execute_query("SELECT SUM(total_quantity) as total FROM Portfolio WHERE stock_id = %s", (stock_id,), fetch='one')
    if holdings and holdings.get('total') and holdings['total'] > 0:
        raise ValueError("Cannot delete stock that is currently held in user portfolios.")
    
    with TransactionScope() as tx:
        stock = tx.execute("SELECT symbol FROM Stocks WHERE stock_id = %s", (stock_id,)).fetchone()
        symbol = stock['symbol'] if stock else f"ID {stock_id}"
        tx.execute("DELETE FROM Watchlist WHERE stock_id = %s", (stock_id,))
        tx.execute("DELETE FROM Stock_Price_History WHERE stock_id = %s", (stock_id,))
        tx.execute("DELETE FROM Stocks WHERE stock_id = %s", (stock_id,))
        tx.execute(
            "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
            (None, 'DELETE_STOCK', 'Stocks', stock_id, f"Deleted stock {symbol}")
        )
