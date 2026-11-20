from services.db import execute_query, execute_update

def get_user_portfolio(user_id):
    query = """
    SELECT 
        p.portfolio_id,
        p.user_id,
        p.stock_id,
        s.symbol,
        s.company_name,
        s.sector,
        p.total_quantity,
        p.average_buy_price,
        s.current_price,
        s.day_change,
        s.day_change_percent,
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
        p.updated_at
    FROM Portfolio p
    JOIN Stocks s ON p.stock_id = s.stock_id
    WHERE p.user_id = %s AND p.total_quantity > 0
    ORDER BY current_value DESC
    """
    holdings = execute_query(query, (user_id,), fetch='all')
    return holdings or []

def get_user_portfolio_summary(user_id):
    user = execute_query("SELECT user_id, name, email, cash_balance FROM Users WHERE user_id = %s", (user_id,), fetch='one')
    if not user:
        return None

    holdings = get_user_portfolio(user_id)
    total_invested = sum(h['total_investment'] for h in holdings)
    total_current_value = sum(h['current_value'] for h in holdings)
    total_pnl = round(total_current_value - total_invested, 2)
    pnl_percent = round((total_pnl / total_invested * 100), 2) if total_invested > 0 else 0.00
    cash_balance = float(user['cash_balance'])
    net_worth = round(cash_balance + total_current_value, 2)

    # Sector distribution for Chart.js
    sector_map = {}
    for h in holdings:
        sec = h['sector']
        sector_map[sec] = round(sector_map.get(sec, 0.0) + float(h['current_value']), 2)

    # Asset distribution for Chart.js
    asset_map = {}
    for h in holdings:
        asset_map[h['symbol']] = float(h['current_value'])

    return {
        'user': user,
        'holdings': holdings,
        'holdings_count': len(holdings),
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_pnl': total_pnl,
        'pnl_percent': pnl_percent,
        'cash_balance': cash_balance,
        'net_worth': net_worth,
        'sector_distribution': sector_map,
        'asset_distribution': asset_map
    }

def get_user_transactions(user_id, stock_id=None, tx_type=None, start_date=None, end_date=None, transaction_id=None):
    query = """
    SELECT 
        t.transaction_id,
        t.user_id,
        t.stock_id,
        s.symbol,
        s.company_name,
        s.sector,
        t.transaction_type,
        t.quantity,
        t.price,
        t.total_amount,
        t.transaction_date,
        t.transaction_time,
        t.transaction_status,
        t.created_at
    FROM Transactions t
    JOIN Stocks s ON t.stock_id = s.stock_id
    WHERE t.user_id = %s
    """
    params = [user_id]
    if transaction_id:
        query += " AND t.transaction_id = %s"
        params.append(transaction_id)
    if stock_id:
        query += " AND t.stock_id = %s"
        params.append(stock_id)
    if tx_type and tx_type != 'ALL':
        query += " AND t.transaction_type = %s"
        params.append(tx_type)
    if start_date:
        query += " AND t.transaction_date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND t.transaction_date <= %s"
        params.append(end_date)
    query += " ORDER BY t.transaction_date DESC, t.transaction_time DESC, t.transaction_id DESC"
    return execute_query(query, params, fetch='all')

def get_user_watchlist(user_id):
    query = """
    SELECT 
        w.watchlist_id,
        w.user_id,
        w.stock_id,
        w.added_at,
        s.symbol,
        s.company_name,
        s.sector,
        s.current_price,
        s.day_change,
        s.day_change_percent,
        s.volume,
        s.high_52w,
        s.low_52w
    FROM Watchlist w
    JOIN Stocks s ON w.stock_id = s.stock_id
    WHERE w.user_id = %s
    ORDER BY s.symbol ASC
    """
    return execute_query(query, (user_id,), fetch='all')

def add_to_watchlist(user_id, stock_id):
    existing = execute_query(
        "SELECT watchlist_id FROM Watchlist WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id),
        fetch='one'
    )
    if existing:
        return {'success': False, 'message': 'Stock is already in your watchlist.'}
    
    execute_update(
        "INSERT INTO Watchlist (user_id, stock_id) VALUES (%s, %s)",
        (user_id, stock_id)
    )
    return {'success': True, 'message': 'Stock added to your watchlist.'}

def remove_from_watchlist(user_id, stock_id):
    execute_update(
        "DELETE FROM Watchlist WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id)
    )
    return {'success': True, 'message': 'Stock removed from your watchlist.'}

def is_in_watchlist(user_id, stock_id):
    row = execute_query(
        "SELECT watchlist_id FROM Watchlist WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id),
        fetch='one'
    )
    return bool(row)
