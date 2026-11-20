import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, flash, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from services.db import execute_query, execute_update, TransactionScope

def get_user_role(user_id):
    """
    Retrieves the active role for a user directly from the database.
    Rechecks on every request to guarantee up-to-date authorization.
    """
    query = """
    SELECT r.role_name 
    FROM User_Roles ur
    JOIN Roles r ON ur.role_id = r.role_id
    WHERE ur.user_id = %s
    ORDER BY ur.role_id ASC
    LIMIT 1
    """
    row = execute_query(query, (user_id,), fetch='one')
    return row['role_name'] if row else 'USER'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Verify account status
        user = execute_query("SELECT account_status FROM Users WHERE user_id = %s", (session['user_id'],), fetch='one')
        if not user or user['account_status'] != 'ACTIVE':
            session.clear()
            flash('Your account has been suspended or closed. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Administrator authentication required.', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        
        role = get_user_role(session['user_id'])
        if role not in ('ADMIN', 'SUPER_ADMIN'):
            flash('Access Denied: Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
            
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Super Administrator authentication required.', 'danger')
            return redirect(url_for('auth.login', next=request.url))
            
        role = get_user_role(session['user_id'])
        if role != 'SUPER_ADMIN':
            flash('Access Denied: Super Administrator privileges required.', 'danger')
            return redirect(url_for('admin.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(email, password):
    user = execute_query("SELECT * FROM Users WHERE email = %s", (email.strip().lower(),), fetch='one')
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def register_user(name, email, phone, password, initial_cash=100000.00):
    """Registers a new user, hashes password, assigns standard USER role, and records audit log."""
    name = name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    
    if not name or not email or not phone or not password:
        return {'success': False, 'message': 'All fields are mandatory.'}
    if len(password) < 6:
        return {'success': False, 'message': 'Password must contain at least 6 characters.'}
        
    existing = execute_query("SELECT user_id FROM Users WHERE email = %s", (email,), fetch='one')
    if existing:
        return {'success': False, 'message': 'An account with this email address is already registered.'}
        
    password_hash = generate_password_hash(password)
    try:
        with TransactionScope() as tx:
            tx.execute("""
                INSERT INTO Users (name, email, phone, password_hash, cash_balance, account_status)
                VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
            """, (name, email, phone, password_hash, initial_cash))
            user_id = tx.lastrowid()
            
            # Role 3 is standard USER
            tx.execute("""
                INSERT INTO User_Roles (user_id, role_id, assigned_by, assigned_at)
                VALUES (%s, 3, NULL, CURRENT_TIMESTAMP)
            """, (user_id,))
            
            tx.execute("""
                INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, new_value, description)
                VALUES (%s, %s, 'USER_REGISTER', 'Users', %s, %s, %s)
            """, (user_id, user_id, user_id, f"Cash: ₹{initial_cash:,.2f}", f"Registered investor account: {email}"))
            
        return {'success': True, 'user_id': user_id, 'message': 'Registration successful.'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def update_user_profile(user_id, name, phone):
    query = "UPDATE Users SET name = %s, phone = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s"
    execute_update(query, (name.strip(), phone.strip(), user_id))
    execute_update(
        "INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s, %s)",
        (user_id, user_id, 'PROFILE_UPDATE', 'Users', user_id, 'Updated contact profile')
    )

def generate_password_reset_token(email):
    user = execute_query("SELECT user_id FROM Users WHERE email = %s", (email.strip().lower(),), fetch='one')
    if not user:
        return None
    token = secrets.token_hex(20)
    token_hash = generate_password_hash(token)
    expiry = datetime.now() + timedelta(hours=1)
    execute_update("""
        INSERT INTO Password_Reset (user_id, reset_token_hash, expiry_time, is_used)
        VALUES (%s, %s, %s, 0)
    """, (user['user_id'], token_hash, expiry))
    return token

def reset_password_with_token(token, new_password):
    if len(new_password) < 6:
        return {'success': False, 'message': 'Password must be at least 6 characters.'}
        
    tokens = execute_query("SELECT * FROM Password_Reset WHERE is_used = 0 AND expiry_time > CURRENT_TIMESTAMP", fetch='all')
    matching_reset = None
    for r in tokens:
        if check_password_hash(r['reset_token_hash'], token):
            matching_reset = r
            break
            
    if not matching_reset:
        return {'success': False, 'message': 'Password reset token is invalid or expired.'}
        
    new_hash = generate_password_hash(new_password)
    with TransactionScope() as tx:
        tx.execute("UPDATE Users SET password_hash = %s WHERE user_id = %s", (new_hash, matching_reset['user_id']))
        tx.execute("UPDATE Password_Reset SET is_used = 1 WHERE reset_id = %s", (matching_reset['reset_id'],))
        tx.execute("""
            INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description)
            VALUES (%s, %s, 'PASSWORD_RESET', 'Users', %s, 'Password reset via token')
        """, (matching_reset['user_id'], matching_reset['user_id'], matching_reset['user_id']))
        
    return {'success': True, 'message': 'Password updated successfully.'}
