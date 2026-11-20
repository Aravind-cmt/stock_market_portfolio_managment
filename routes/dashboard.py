from flask import Blueprint, render_template, session
from routes.auth import login_required
from services.portfolio_service import get_user_portfolio_summary, get_user_transactions
from services.market_service import get_market_summary

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    summary = get_user_portfolio_summary(user_id)
    recent_transactions = get_user_transactions(user_id)[:5]
    market = get_market_summary()
    
    return render_template(
        'dashboard/index.html',
        summary=summary,
        recent_transactions=recent_transactions,
        market=market
    )
