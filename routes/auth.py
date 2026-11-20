import secrets
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from services.db import execute_query, execute_update, TransactionScope
from services.auth_service import login_required, get_user_role, authenticate_user, update_user_profile
from config import Config

auth_bp = Blueprint('auth', __name__)

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
            flash('All fields are mandatory.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        if len(password) < 6:
            flash('Password must be at least 6 characters in length.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        existing_user = execute_query("SELECT user_id FROM Users WHERE email = %s", (email,), fetch='one')
        if existing_user:
            flash('An account with this email address is already registered. Please sign in.', 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        password_hash = generate_password_hash(password)
        try:
            with TransactionScope() as tx:
                # 1. Insert user
                tx.execute("""
                    INSERT INTO Users (name, email, phone, password_hash, cash_balance, account_status)
                    VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
                """, (name, email, phone, password_hash, Config.INITIAL_CASH_BALANCE))
                user_id = tx.lastrowid()

                # 2. Assign standard USER role (role_id 3)
                tx.execute("""
                    INSERT INTO User_Roles (user_id, role_id, assigned_by, assigned_at)
                    VALUES (%s, 3, NULL, CURRENT_TIMESTAMP)
                """, (user_id,))

                # 3. Audit log
                tx.execute("""
                    INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, new_value, description)
                    VALUES (%s, %s, 'USER_REGISTER', 'Users', %s, %s, %s)
                """, (user_id, user_id, user_id, f"Cash: ₹{Config.INITIAL_CASH_BALANCE:,.2f}", f"Registered investor account: {email}"))

            flash(f'Account created successfully. Welcome bonus of ₹{Config.INITIAL_CASH_BALANCE:,.2f} paper trading balance has been credited.', 'success')
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

        user = authenticate_user(email, password)
        if user:
            if user['account_status'] != 'ACTIVE':
                flash('Your account has been suspended or closed. Contact support.', 'danger')
                return render_template('auth/login.html')

            session.clear()
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            
            # Fetch and store current user role
            role = get_user_role(user['user_id'])
            session['user_role'] = role
            session['is_admin'] = role in ('ADMIN', 'SUPER_ADMIN')
            session['is_super_admin'] = role == 'SUPER_ADMIN'

            execute_update(
                "INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s, %s)",
                (user['user_id'], user['user_id'], 'USER_LOGIN', 'Users', user['user_id'], f"User {user['email']} authenticated successfully with role {role}")
            )

            flash(f'Welcome back, {user["name"]}.', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if role in ('ADMIN', 'SUPER_ADMIN'):
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email address or password. Please verify and try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        execute_update(
            "INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, user_id, 'USER_LOGOUT', 'Users', user_id, "User session ended")
        )
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        if not name or not phone:
            flash('Name and phone number cannot be blank.', 'danger')
        else:
            update_user_profile(user_id, name, phone)
            session['user_name'] = name
            flash('Profile details updated successfully.', 'success')
            return redirect(url_for('auth.profile'))

    user = execute_query("SELECT user_id, name, email, phone, cash_balance, account_status, created_at FROM Users WHERE user_id = %s", (user_id,), fetch='one')
    role = get_user_role(user_id)
    return render_template('auth/profile.html', user=user, role=role)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = execute_query("SELECT user_id, name FROM Users WHERE email = %s", (email,), fetch='one')
        if user:
            token = secrets.token_hex(20)
            token_hash = generate_password_hash(token)
            expiry = datetime.now() + timedelta(hours=1)
            execute_update("""
                INSERT INTO Password_Reset (user_id, reset_token_hash, expiry_time, is_used)
                VALUES (%s, %s, %s, 0)
            """, (user['user_id'], token_hash, expiry))
            flash(f'Recovery token generated. For testing demonstration, use reset link: /reset-password/{token}', 'info')
        else:
            flash('If an account exists with that email address, password recovery instructions have been dispatched.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Search unused and unexpired reset tokens
    tokens = execute_query("SELECT * FROM Password_Reset WHERE is_used = 0 AND expiry_time > CURRENT_TIMESTAMP", fetch='all')
    matching_reset = None
    for r in tokens:
        if check_password_hash(r['reset_token_hash'], token):
            matching_reset = r
            break

    if not matching_reset:
        flash('Password reset token is invalid or has expired. Please request a new token.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if len(new_password) < 6:
            flash('Password must be at least 6 characters in length.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        new_hash = generate_password_hash(new_password)
        with TransactionScope() as tx:
            tx.execute("UPDATE Users SET password_hash = %s WHERE user_id = %s", (new_hash, matching_reset['user_id']))
            tx.execute("UPDATE Password_Reset SET is_used = 1 WHERE reset_id = %s", (matching_reset['reset_id'],))
            tx.execute("""
                INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description)
                VALUES (%s, %s, 'PASSWORD_RESET', 'Users', %s, 'User reset password via token recovery')
            """, (matching_reset['user_id'], matching_reset['user_id'], matching_reset['user_id']))

        flash('Your password has been successfully reset. Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        user = execute_query("SELECT password_hash FROM Users WHERE user_id = %s", (session['user_id'],), fetch='one')
        if not check_password_hash(user['password_hash'], current_password):
            flash('Current password verified incorrectly.', 'danger')
            return render_template('auth/change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')

        if len(new_password) < 6:
            flash('New password must contain at least 6 characters.', 'danger')
            return render_template('auth/change_password.html')

        new_hash = generate_password_hash(new_password)
        execute_update("UPDATE Users SET password_hash = %s WHERE user_id = %s", (new_hash, session['user_id']))
        execute_update(
            "INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (session['user_id'], session['user_id'], 'PASSWORD_CHANGE', 'Users', session['user_id'], 'User changed account password')
        )
        flash('Password updated successfully.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
