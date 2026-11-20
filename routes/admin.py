from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import admin_required, super_admin_required, get_user_role
from services.db import execute_query, execute_update
from services.admin_service import (
    get_all_administrators, get_promotable_users, promote_user_to_admin,
    demote_admin_to_user, get_admin_metrics
)
from services.market_service import (
    get_all_stocks, get_stock_by_id, add_stock, update_stock,
    update_stock_price, delete_stock, get_sectors
)
from services.audit_service import get_all_audit_logs

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login')
def login():
    # If already logged in with admin role, redirect to dashboard
    if 'user_id' in session:
        role = get_user_role(session['user_id'])
        if role in ('ADMIN', 'SUPER_ADMIN'):
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    metrics = get_admin_metrics()
    role = get_user_role(session['user_id'])
    return render_template('admin/index.html', metrics=metrics, user_role=role)

# -----------------------------------------------------------------------------
# Super Admin: Dedicated Admin Management Section
# -----------------------------------------------------------------------------
@admin_bp.route('/admins')
@super_admin_required
def admin_management():
    admins = get_all_administrators()
    return render_template('admin/admin_management.html', admins=admins)

@admin_bp.route('/admins/add', methods=['GET', 'POST'])
@super_admin_required
def add_admin():
    search = request.args.get('search', '').strip()
    promotable_users = get_promotable_users(search=search)

    if request.method == 'POST':
        target_user_id = request.form.get('target_user_id', type=int)
        if not target_user_id:
            flash('Please select an active investor to promote.', 'danger')
            return redirect(url_for('admin.add_admin'))

        res = promote_user_to_admin(session['user_id'], target_user_id)
        if res['success']:
            flash(res['message'], 'success')
            return redirect(url_for('admin.admin_management'))
        else:
            flash(res['message'], 'danger')

    return render_template('admin/add_admin.html', users=promotable_users, search=search)

@admin_bp.route('/admins/remove/<int:target_user_id>', methods=['POST'])
@super_admin_required
def remove_admin(target_user_id):
    res = demote_admin_to_user(session['user_id'], target_user_id)
    if res['success']:
        flash(res['message'], 'info')
    else:
        flash(res['message'], 'danger')
    return redirect(url_for('admin.admin_management'))

# -----------------------------------------------------------------------------
# Stock Registry Management
# -----------------------------------------------------------------------------
@admin_bp.route('/stocks')
@admin_required
def stocks():
    stocks_list = get_all_stocks()
    sectors = get_sectors()
    return render_template('admin/stocks.html', stocks=stocks_list, sectors=sectors)

@admin_bp.route('/stocks/add', methods=['POST'])
@admin_required
def stock_add():
    symbol = request.form.get('symbol', '').strip().upper()
    company_name = request.form.get('company_name', '').strip()
    sector = request.form.get('sector', '').strip()
    current_price = request.form.get('current_price')
    high_52w = request.form.get('high_52w')
    low_52w = request.form.get('low_52w')

    try:
        add_stock(symbol, company_name, sector, current_price, high_52w, low_52w, acting_user_id=session['user_id'])
        flash(f'Stock {symbol} added to market registry successfully.', 'success')
    except Exception as e:
        flash(f'Error adding stock: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

@admin_bp.route('/stocks/edit/<int:stock_id>', methods=['POST'])
@admin_required
def stock_edit(stock_id):
    company_name = request.form.get('company_name', '').strip()
    sector = request.form.get('sector', '').strip()
    high_52w = request.form.get('high_52w')
    low_52w = request.form.get('low_52w')

    try:
        update_stock(stock_id, company_name, sector, high_52w, low_52w, acting_user_id=session['user_id'])
        flash('Stock details updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

@admin_bp.route('/stocks/price-update/<int:stock_id>', methods=['POST'])
@admin_required
def stock_price_update(stock_id):
    new_price = request.form.get('new_price')
    try:
        update_stock_price(stock_id, new_price, acting_user_id=session['user_id'])
        flash('Stock price updated and historical tick archived.', 'success')
    except Exception as e:
        flash(f'Error updating price: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

@admin_bp.route('/stocks/delete/<int:stock_id>', methods=['POST'])
@admin_required
def stock_delete(stock_id):
    try:
        delete_stock(stock_id, acting_user_id=session['user_id'])
        flash('Stock removed from market registry.', 'success')
    except Exception as e:
        flash(f'Cannot delete stock: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

# -----------------------------------------------------------------------------
# User & Account Oversight
# -----------------------------------------------------------------------------
@admin_bp.route('/users')
@admin_required
def users():
    users_list = execute_query("""
        SELECT u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at,
               r.role_name,
               COUNT(DISTINCT p.stock_id) as stocks_held,
               COALESCE(SUM(p.total_quantity * p.average_buy_price), 0) as total_invested
        FROM Users u
        JOIN User_Roles ur ON u.user_id = ur.user_id
        JOIN Roles r ON ur.role_id = r.role_id
        LEFT JOIN Portfolio p ON u.user_id = p.user_id AND p.total_quantity > 0
        GROUP BY u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at, r.role_name
        ORDER BY u.user_id ASC
    """, fetch='all')
    role = get_user_role(session['user_id'])
    return render_template('admin/users.html', users=users_list, user_role=role)

@admin_bp.route('/users/status/<int:target_user_id>', methods=['POST'])
@admin_required
def toggle_user_status(target_user_id):
    target = execute_query("SELECT user_id, name, account_status FROM Users WHERE user_id = %s", (target_user_id,), fetch='one')
    if not target:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))

    target_role = get_user_role(target_user_id)
    if target_role == 'SUPER_ADMIN':
        flash('Security Violation: Cannot modify status of a Super Administrator.', 'danger')
        return redirect(url_for('admin.users'))

    new_status = 'SUSPENDED' if target['account_status'] == 'ACTIVE' else 'ACTIVE'
    execute_update("UPDATE Users SET account_status = %s WHERE user_id = %s", (new_status, target_user_id))
    execute_update(
        "INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (session['user_id'], target_user_id, 'STATUS_CHANGE', 'Users', target_user_id, target['account_status'], new_status, f"Changed account status for {target['name']} to {new_status}")
    )
    flash(f"Account status for {target['name']} updated to {new_status}.", 'info')
    return redirect(url_for('admin.users'))

# -----------------------------------------------------------------------------
# System Ledger & Audit Trail
# -----------------------------------------------------------------------------
@admin_bp.route('/transactions')
@admin_required
def transactions():
    all_tx = execute_query("""
        SELECT t.*, u.name as user_name, u.email as user_email, s.symbol, s.company_name
        FROM Transactions t
        JOIN Users u ON t.user_id = u.user_id
        JOIN Stocks s ON t.stock_id = s.stock_id
        ORDER BY t.transaction_id DESC
    """, fetch='all')
    return render_template('admin/transactions.html', transactions=all_tx)

@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    logs = get_all_audit_logs(limit=100)
    return render_template('admin/audit_logs.html', logs=logs)
