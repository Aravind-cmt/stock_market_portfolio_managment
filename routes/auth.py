from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from services.db import execute_query, execute_update
from config import Config

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Administrator authentication required.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not email or not phone or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        existing_user = execute_query("SELECT user_id FROM Users WHERE email = %s", (email,), fetch='one')
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        password_hash = generate_password_hash(password)
        try:
            user_id = execute_update("""
                INSERT INTO Users (name, email, phone, password_hash, cash_balance, account_status)
                VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
            """, (name, email, phone, password_hash, Config.INITIAL_CASH_BALANCE))

            # Audit log
            execute_update(
                "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
                (user_id, 'USER_REGISTER', 'Users', user_id, f"Registered new account: {email}")
            )

            flash(f'Account created successfully! Welcome bonus ₹{Config.INITIAL_CASH_BALANCE:,.2f} paper cash added.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')

        user = execute_query("SELECT * FROM Users WHERE email = %s", (email,), fetch='one')
        if user and check_password_hash(user['password_hash'], password):
            if user['account_status'] != 'ACTIVE':
                flash('Your account has been suspended or closed. Contact support.', 'danger')
                return render_template('auth/login.html')

            session.clear()
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']

            execute_update(
                "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
                (user['user_id'], 'USER_LOGIN', 'Users', user['user_id'], f"User {user['email']} logged in")
            )

            flash(f'Welcome back, {user["name"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        execute_update(
            "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
            (user_id, 'USER_LOGOUT', 'Users', user_id, "User logged out")
        )
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = execute_query("SELECT user_id, name FROM Users WHERE email = %s", (email,), fetch='one')
        if user:
            import secrets
            from datetime import datetime, timedelta
            token = secrets.token_hex(16)
            token_hash = generate_password_hash(token)
            expiry = datetime.now() + timedelta(hours=1)
            execute_update("""
                INSERT INTO Password_Reset (user_id, reset_token_hash, expiry_time, is_used)
                VALUES (%s, %s, %s, 0)
            """, (user['user_id'], token_hash, expiry))
            flash('Password reset link simulated. For demonstration, your token is: ' + token[:8] + '... Contact administrator to complete reset.', 'info')
        else:
            flash('If an account exists with that email, reset instructions have been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        user = execute_query("SELECT password_hash FROM Users WHERE user_id = %s", (session['user_id'],), fetch='one')
        if not check_password_hash(user['password_hash'], current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')

        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/change_password.html')

        new_hash = generate_password_hash(new_password)
        execute_update("UPDATE Users SET password_hash = %s WHERE user_id = %s", (new_hash, session['user_id']))
        execute_update(
            "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
            (session['user_id'], 'PASSWORD_CHANGE', 'Users', session['user_id'], "User updated password")
        )
        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
