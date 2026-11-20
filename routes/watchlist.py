from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth import login_required
from services.portfolio_service import get_user_watchlist, add_to_watchlist, remove_from_watchlist, get_user_portfolio_summary

watchlist_bp = Blueprint('watchlist', __name__)

@watchlist_bp.route('/watchlist')
@login_required
def index():
    user_id = session['user_id']
    watchlist = get_user_watchlist(user_id)
    summary = get_user_portfolio_summary(user_id)
    cash_balance = summary['cash_balance'] if summary else 0.0
    return render_template('watchlist/index.html', watchlist=watchlist, cash_balance=cash_balance)

@watchlist_bp.route('/watchlist/add/<int:stock_id>', methods=['POST'])
@login_required
def add(stock_id):
    user_id = session['user_id']
    res = add_to_watchlist(user_id, stock_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(res)
    flash(res['message'], 'success' if res['success'] else 'info')
    return redirect(request.referrer or url_for('watchlist.index'))

@watchlist_bp.route('/watchlist/remove/<int:stock_id>', methods=['POST'])
@login_required
def remove(stock_id):
    user_id = session['user_id']
    res = remove_from_watchlist(user_id, stock_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(res)
    flash(res['message'], 'info')
    return redirect(request.referrer or url_for('watchlist.index'))
