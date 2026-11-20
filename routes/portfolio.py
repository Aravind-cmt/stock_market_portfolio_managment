from flask import Blueprint, render_template, session
from routes.auth import login_required
from services.portfolio_service import get_user_portfolio_summary

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/portfolio')
@login_required
def index():
    user_id = session['user_id']
    summary = get_user_portfolio_summary(user_id)
    return render_template('portfolio/index.html', summary=summary)
