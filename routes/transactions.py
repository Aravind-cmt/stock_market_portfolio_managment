from flask import Blueprint, render_template, request, session
from routes.auth import login_required
from services.portfolio_service import get_user_transactions
from services.market_service import get_all_stocks

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    user_id = session['user_id']
    stock_id = request.args.get('stock_id', type=int)
    tx_type = request.args.get('type', 'ALL')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    transactions = get_user_transactions(
        user_id,
        stock_id=stock_id,
        tx_type=tx_type,
        start_date=start_date,
        end_date=end_date
    )
    stocks = get_all_stocks()

    return render_template(
        'transactions/index.html',
        transactions=transactions,
        stocks=stocks,
        selected_stock_id=stock_id,
        selected_type=tx_type,
        start_date=start_date,
        end_date=end_date
    )
