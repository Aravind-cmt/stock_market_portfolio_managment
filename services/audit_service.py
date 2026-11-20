from services.db import execute_query, execute_update

def log_action(user_id, action, table_name, record_id, description):
    query = """
    INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
    VALUES (%s, %s, %s, %s, %s)
    """
    execute_update(query, (user_id, action, table_name, record_id, description))

def get_all_audit_logs(limit=50):
    query = """
    SELECT 
        a.log_id,
        a.user_id,
        u.name AS user_name,
        u.email AS user_email,
        a.action,
        a.table_name,
        a.record_id,
        a.action_timestamp,
        a.description
    FROM Audit_Log a
    LEFT JOIN Users u ON a.user_id = u.user_id
    ORDER BY a.action_timestamp DESC, a.log_id DESC
    LIMIT %s
    """
    return execute_query(query, (limit,), fetch='all')

def get_admin_system_metrics():
    total_users = execute_query("SELECT COUNT(*) AS count FROM Users", fetch='one')['count']
    total_stocks = execute_query("SELECT COUNT(*) AS count FROM Stocks", fetch='one')['count']
    total_transactions = execute_query("SELECT COUNT(*) AS count FROM Transactions", fetch='one')['count']
    total_volume = execute_query("SELECT COALESCE(SUM(total_amount), 0) AS total FROM Transactions", fetch='one')['total']
    
    recent_transactions = execute_query("""
        SELECT t.*, u.name as user_name, s.symbol 
        FROM Transactions t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Stocks s ON t.stock_id = s.stock_id
        ORDER BY t.transaction_id DESC LIMIT 10
    """, fetch='all')

    users_list = execute_query("""
        SELECT u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at,
               COUNT(DISTINCT p.stock_id) as stocks_owned,
               COALESCE(SUM(p.total_quantity * p.average_buy_price), 0) as total_invested
        FROM Users u
        LEFT JOIN Portfolio p ON u.user_id = p.user_id AND p.total_quantity > 0
        GROUP BY u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at
        ORDER BY u.user_id ASC
    """, fetch='all')

    return {
        'total_users': total_users,
        'total_stocks': total_stocks,
        'total_transactions': total_transactions,
        'total_volume': total_volume,
        'recent_transactions': recent_transactions,
        'users_list': users_list
    }
