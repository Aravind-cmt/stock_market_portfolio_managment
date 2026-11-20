from flask import Blueprint, jsonify, request, session
from services.market_service import get_all_stocks, get_stock_by_id, get_stock_price_history
from services.portfolio_service import get_user_portfolio_summary, add_to_watchlist, remove_from_watchlist, is_in_watchlist
from services.db import get_db_mode

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/db-status')
def db_status():
    mode = get_db_mode()
    return jsonify({
        'engine': mode,
        'status': 'connected',
        'is_mysql': mode == 'mysql'
    })

@api_bp.route('/stocks')
def list_stocks():
    search = request.args.get('search')
    sector = request.args.get('sector')
    stocks = get_all_stocks(search=search, sector=sector)
    return jsonify(stocks)

@api_bp.route('/stocks/<int:stock_id>')
def get_stock(stock_id):
    stock = get_stock_by_id(stock_id)
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    return jsonify(stock)

@api_bp.route('/stocks/<int:stock_id>/history')
def get_price_history(stock_id):
    limit = request.args.get('limit', default=20, type=int)
    history = get_stock_price_history(stock_id, limit=limit)
    labels = []
    prices = []
    for h in history:
        labels.append(str(h['recorded_at'])[:16])
        prices.append(float(h['price']))
    return jsonify({
        'stock_id': stock_id,
        'labels': labels,
        'prices': prices
    })

@api_bp.route('/portfolio/charts')
def portfolio_charts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    summary = get_user_portfolio_summary(session['user_id'])
    if not summary:
        return jsonify({'sectors': {}, 'assets': {}})
    return jsonify({
        'sectors': summary['sector_distribution'],
        'assets': summary['asset_distribution'],
        'total_invested': summary['total_invested'],
        'total_value': summary['total_current_value'],
        'total_pnl': summary['total_pnl']
    })

@api_bp.route('/watchlist/toggle/<int:stock_id>', methods=['POST'])
def toggle_watchlist(stock_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to manage watchlist'}), 401
    user_id = session['user_id']
    if is_in_watchlist(user_id, stock_id):
        res = remove_from_watchlist(user_id, stock_id)
        res['in_watchlist'] = False
    else:
        res = add_to_watchlist(user_id, stock_id)
        res['in_watchlist'] = True
    return jsonify(res)
