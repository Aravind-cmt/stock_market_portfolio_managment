from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from routes.auth import admin_required
from services.db import execute_query, execute_update
from services.market_service import get_all_stocks, get_stock_by_id, add_stock, update_stock, update_stock_price, delete_stock, get_sectors
from services.audit_service import get_all_audit_logs, get_admin_system_metrics

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        admin = execute_query("SELECT * FROM Admin WHERE email = %s", (email,), fetch='one')
        if admin and check_password_hash(admin['password_hash'], password):
            session.clear()
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            session['admin_role'] = admin['role']
            session['is_admin'] = True

            execute_update(
                "INSERT INTO Audit_Log (user_id, action, table_name, record_id, description) VALUES (%s, %s, %s, %s, %s)",
                (None, 'ADMIN_LOGIN', 'Admin', admin['admin_id'], f"Admin {admin['username']} logged in")
            )

            flash(f'Admin authentication successful. Welcome, {admin["username"]}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid administrator credentials.', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    metrics = get_admin_system_metrics()
    return render_template('admin/index.html', metrics=metrics)

@admin_bp.route('/users')
@admin_required
def users():
    users_list = execute_query("""
        SELECT u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at,
               COUNT(DISTINCT p.stock_id) as stocks_held,
               COALESCE(SUM(p.total_quantity * p.average_buy_price), 0) as total_invested
        FROM Users u
        LEFT JOIN Portfolio p ON u.user_id = p.user_id AND p.total_quantity > 0
        GROUP BY u.user_id, u.name, u.email, u.phone, u.cash_balance, u.account_status, u.created_at
        ORDER BY u.user_id ASC
    """, fetch='all')
    return render_template('admin/users.html', users=users_list)

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
        add_stock(symbol, company_name, sector, current_price, high_52w, low_52w)
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
        update_stock(stock_id, company_name, sector, high_52w, low_52w)
        flash('Stock details updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating stock: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

@admin_bp.route('/stocks/price-update/<int:stock_id>', methods=['POST'])
@admin_required
def stock_price_update(stock_id):
    new_price = request.form.get('new_price')
    try:
        update_stock_price(stock_id, new_price)
        flash('Stock price updated and historical tick archived.', 'success')
    except Exception as e:
        flash(f'Error updating price: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

@admin_bp.route('/stocks/delete/<int:stock_id>', methods=['POST'])
@admin_required
def stock_delete(stock_id):
    try:
        delete_stock(stock_id)
        flash('Stock removed from market registry.', 'success')
    except Exception as e:
        flash(f'Cannot delete stock: {str(e)}', 'danger')
    return redirect(url_for('admin.stocks'))

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
