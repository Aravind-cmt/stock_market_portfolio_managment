from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth import login_required
from services.trade_service import execute_buy, execute_sell
from services.market_service import get_all_stocks, get_stock_by_id
from services.portfolio_service import get_user_portfolio_summary

trade_bp = Blueprint('trade', __name__)

@trade_bp.route('/trade', methods=['GET'])
@login_required
def index():
    selected_stock_id = request.args.get('stock_id', type=int)
    action = request.args.get('action', 'buy').lower()
    
    user_id = session['user_id']
    stocks = get_all_stocks()
    summary = get_user_portfolio_summary(user_id)
    
    selected_stock = get_stock_by_id(selected_stock_id) if selected_stock_id else (stocks[0] if stocks else None)
    
    owned_quantity = 0
    if selected_stock and summary:
        for h in summary['holdings']:
            if h['stock_id'] == selected_stock['stock_id']:
                owned_quantity = h['total_quantity']
                break

    return render_template(
        'trade/buy_sell.html',
        stocks=stocks,
        selected_stock=selected_stock,
        action=action,
        summary=summary,
        owned_quantity=owned_quantity
    )

@trade_bp.route('/trade/buy', methods=['POST'])
@login_required
def buy():
    user_id = session['user_id']
    stock_id = request.form.get('stock_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if not stock_id or not quantity or quantity <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid stock or quantity.'}), 400
        flash('Invalid stock or quantity provided.', 'danger')
        return redirect(request.referrer or url_for('market.index'))

    result = execute_buy(user_id, stock_id, quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result), (200 if result['success'] else 400)

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(request.referrer or url_for('portfolio.index'))

@trade_bp.route('/trade/sell', methods=['POST'])
@login_required
def sell():
    user_id = session['user_id']
    stock_id = request.form.get('stock_id', type=int)
    quantity = request.form.get('quantity', type=int)

    if not stock_id or not quantity or quantity <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid stock or quantity.'}), 400
        flash('Invalid stock or quantity provided.', 'danger')
        return redirect(request.referrer or url_for('portfolio.index'))

    result = execute_sell(user_id, stock_id, quantity)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result), (200 if result['success'] else 400)

    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(request.referrer or url_for('portfolio.index'))
