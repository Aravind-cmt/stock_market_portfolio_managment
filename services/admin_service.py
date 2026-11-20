from services.db import execute_query, execute_update, TransactionScope

def get_all_administrators():
    query = """
    SELECT 
        u.user_id,
        u.name,
        u.email,
        u.phone,
        u.account_status,
        u.created_at,
        r.role_name,
        ur.assigned_at,
        assigner.name AS assigned_by_name
    FROM Users u
    JOIN User_Roles ur ON u.user_id = ur.user_id
    JOIN Roles r ON ur.role_id = r.role_id
    LEFT JOIN Users assigner ON ur.assigned_by = assigner.user_id
    WHERE r.role_name IN ('SUPER_ADMIN', 'ADMIN')
    ORDER BY ur.role_id ASC, u.user_id ASC
    """
    return execute_query(query, fetch='all')

def get_promotable_users(search=None):
    query = """
    SELECT 
        u.user_id,
        u.name,
        u.email,
        u.phone,
        u.account_status,
        u.created_at,
        r.role_name
    FROM Users u
    JOIN User_Roles ur ON u.user_id = ur.user_id
    JOIN Roles r ON ur.role_id = r.role_id
    WHERE r.role_name = 'USER' AND u.account_status = 'ACTIVE'
    """
    params = []
    if search:
        query += " AND (u.name LIKE %s OR u.email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY u.name ASC LIMIT 50"
    return execute_query(query, params, fetch='all')

def promote_user_to_admin(acting_user_id, target_user_id):
    """
    Promotes an active registered user with role USER to role ADMIN.
    Restricted to SUPER_ADMIN on backend.
    """
    with TransactionScope() as tx:
        # 1. Verify acting user is SUPER_ADMIN
        actor = tx.execute("""
            SELECT r.role_name 
            FROM User_Roles ur
            JOIN Roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = %s
        """, (acting_user_id,)).fetchone()

        if not actor or actor['role_name'] != 'SUPER_ADMIN':
            return {'success': False, 'message': 'Unauthorized: Only Super Administrators can promote users.'}

        # 2. Verify target user
        target = tx.execute("""
            SELECT u.user_id, u.name, u.email, r.role_name
            FROM Users u
            JOIN User_Roles ur ON u.user_id = ur.user_id
            JOIN Roles r ON ur.role_id = r.role_id
            WHERE u.user_id = %s
        """, (target_user_id,)).fetchone()

        if not target:
            return {'success': False, 'message': 'Target user not found.'}

        if target['role_name'] == 'ADMIN':
            return {'success': False, 'message': f"{target['name']} is already an Administrator."}

        if target['role_name'] == 'SUPER_ADMIN':
            return {'success': False, 'message': 'Cannot modify Super Administrator.'}

        # 3. Get ADMIN role_id (2)
        admin_role = tx.execute("SELECT role_id FROM Roles WHERE role_name = 'ADMIN'").fetchone()
        role_id = admin_role['role_id']

        # 4. Update User_Roles
        tx.execute("DELETE FROM User_Roles WHERE user_id = %s", (target_user_id,))
        tx.execute("""
            INSERT INTO User_Roles (user_id, role_id, assigned_by, assigned_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (target_user_id, role_id, acting_user_id))

        # 5. Record in Audit_Log
        tx.execute("""
            INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description)
            VALUES (%s, %s, 'ROLE_CHANGE', 'User_Roles', %s, 'USER', 'ADMIN', %s)
        """, (
            acting_user_id, target_user_id, target_user_id,
            f"Super Admin promoted {target['name']} ({target['email']}) to Administrator."
        ))

        return {'success': True, 'message': f"User {target['name']} successfully promoted to Administrator."}

def demote_admin_to_user(acting_user_id, target_user_id):
    """
    Revokes Administrator privileges and changes role back to USER.
    Prevents removing or demoting the last active Super Admin.
    """
    with TransactionScope() as tx:
        # 1. Verify acting user is SUPER_ADMIN
        actor = tx.execute("""
            SELECT r.role_name 
            FROM User_Roles ur
            JOIN Roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = %s
        """, (acting_user_id,)).fetchone()

        if not actor or actor['role_name'] != 'SUPER_ADMIN':
            return {'success': False, 'message': 'Unauthorized: Only Super Administrators can revoke admin privileges.'}

        # 2. Check target role
        target = tx.execute("""
            SELECT u.user_id, u.name, u.email, r.role_name
            FROM Users u
            JOIN User_Roles ur ON u.user_id = ur.user_id
            JOIN Roles r ON ur.role_id = r.role_id
            WHERE u.user_id = %s
        """, (target_user_id,)).fetchone()

        if not target:
            return {'success': False, 'message': 'Target user not found.'}

        # Prevent removing or demoting last Super Admin
        if target['role_name'] == 'SUPER_ADMIN':
            super_count = tx.execute("""
                SELECT COUNT(*) as count 
                FROM User_Roles ur
                JOIN Roles r ON ur.role_id = r.role_id
                WHERE r.role_name = 'SUPER_ADMIN'
            """).fetchone()

            if super_count['count'] <= 1:
                return {'success': False, 'message': 'Operation Prevented: Cannot demote the last remaining active Super Administrator.'}

        # 3. Get USER role_id (3)
        user_role = tx.execute("SELECT role_id FROM Roles WHERE role_name = 'USER'").fetchone()
        role_id = user_role['role_id']

        # 4. Update User_Roles
        tx.execute("DELETE FROM User_Roles WHERE user_id = %s", (target_user_id,))
        tx.execute("""
            INSERT INTO User_Roles (user_id, role_id, assigned_by, assigned_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (target_user_id, role_id, acting_user_id))

        # 5. Record in Audit_Log
        tx.execute("""
            INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description)
            VALUES (%s, %s, 'ROLE_CHANGE', 'User_Roles', %s, %s, 'USER', %s)
        """, (
            acting_user_id, target_user_id, target_user_id, target['role_name'],
            f"Super Admin revoked admin privileges for {target['name']}; demoted to USER."
        ))

        return {'success': True, 'message': f"Administrator privileges revoked for {target['name']}."}

def get_admin_metrics():
    total_users = execute_query("SELECT COUNT(*) AS count FROM Users", fetch='one')['count']
    total_stocks = execute_query("SELECT COUNT(*) AS count FROM Stocks", fetch='one')['count']
    total_admins = execute_query("""
        SELECT COUNT(*) AS count 
        FROM User_Roles ur
        JOIN Roles r ON ur.role_id = r.role_id
        WHERE r.role_name IN ('SUPER_ADMIN', 'ADMIN')
    """, fetch='one')['count']
    
    total_tx = execute_query("SELECT COUNT(*) AS count FROM Transactions", fetch='one')['count']
    total_buy = execute_query("SELECT COUNT(*) AS count FROM Transactions WHERE transaction_type = 'BUY'", fetch='one')['count']
    total_sell = execute_query("SELECT COUNT(*) AS count FROM Transactions WHERE transaction_type = 'SELL'", fetch='one')['count']
    total_volume = execute_query("SELECT COALESCE(SUM(total_amount), 0) AS total FROM Transactions", fetch='one')['total']

    recent_transactions = execute_query("""
        SELECT t.*, u.name as user_name, s.symbol 
        FROM Transactions t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Stocks s ON t.stock_id = s.stock_id
        ORDER BY t.transaction_id DESC LIMIT 10
    """, fetch='all')

    recent_users = execute_query("""
        SELECT u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at,
               r.role_name
        FROM Users u
        JOIN User_Roles ur ON u.user_id = ur.user_id
        JOIN Roles r ON ur.role_id = r.role_id
        ORDER BY u.user_id DESC LIMIT 8
    """, fetch='all')

    return {
        'total_users': total_users,
        'total_stocks': total_stocks,
        'total_admins': total_admins,
        'total_transactions': total_tx,
        'total_buy_transactions': total_buy,
        'total_sell_transactions': total_sell,
        'total_volume': total_volume,
        'recent_transactions': recent_transactions,
        'recent_users': recent_users
    }
