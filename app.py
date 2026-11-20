import os
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from services.db import get_db_mode, execute_query
from services.auth_service import get_user_role
from database.setup_database import init_db

# Initialize blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.market import market_bp
from routes.trade import trade_bp
from routes.portfolio import portfolio_bp
from routes.watchlist import watchlist_bp
from routes.transactions import transactions_bp
from routes.reports import reports_bp
from routes.admin import admin_bp
from routes.api import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(market_bp)
app.register_blueprint(trade_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(watchlist_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

@app.context_processor
def inject_global_variables():
    """
    Injects contextual information into Jinja2 templates:
    user profile, current cash balance, active role, db mode status.
    Rechecked from the database on every request.
    """
    user_data = None
    cash_balance = 0.00
    user_role = 'GUEST'
    
    if 'user_id' in session:
        user_data = execute_query(
            "SELECT user_id, name, email, cash_balance, account_status FROM Users WHERE user_id = %s",
            (session['user_id'],),
            fetch='one'
        )
        if user_data:
            cash_balance = float(user_data['cash_balance'])
            user_role = get_user_role(session['user_id'])
            # Keep session updated
            session['user_role'] = user_role
            session['is_admin'] = user_role in ('ADMIN', 'SUPER_ADMIN')
            session['is_super_admin'] = user_role == 'SUPER_ADMIN'

    return {
        'current_user': user_data,
        'user_cash_balance': cash_balance,
        'user_role': user_role,
        'is_admin': user_role in ('ADMIN', 'SUPER_ADMIN'),
        'is_super_admin': user_role == 'SUPER_ADMIN',
        'db_mode': get_db_mode()
    }

@app.route('/')
def landing():
    if 'user_id' in session:
        role = get_user_role(session['user_id'])
        if role in ('ADMIN', 'SUPER_ADMIN'):
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="<div class='container py-5 text-center'><h3>404 - Page Not Found</h3><p class='text-secondary'>The requested endpoint does not exist.</p><a href='/' class='btn btn-primary btn-sm'>Return to Home</a></div>"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', content="<div class='container py-5 text-center text-danger'><h3>500 - Internal Server Error</h3><p class='text-secondary'>A database or system execution error occurred.</p><a href='/' class='btn btn-primary btn-sm'>Return to Home</a></div>"), 500

if __name__ == '__main__':
    # Initialize schema on startup if needed
    try:
        init_db()
    except Exception as e:
        print(f"[Warning] Init DB: {e}")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
