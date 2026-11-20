from flask import Blueprint, render_template, request, session
from services.market_service import get_all_stocks, get_stock_by_id, get_sectors, get_stock_price_history
from services.portfolio_service import get_user_watchlist, get_user_portfolio_summary

market_bp = Blueprint('market', __name__)

@market_bp.route('/market')
def index():
    search = request.args.get('search', '').strip()
    sector = request.args.get('sector', 'ALL')
    sort_by = request.args.get('sort', 'symbol_asc')
    
    stocks = get_all_stocks(search=search, sector=sector, sort_by=sort_by)
    sectors = get_sectors()
    
    watchlist_stock_ids = []
    cash_balance = 0.0
    if 'user_id' in session:
        watchlist = get_user_watchlist(session['user_id'])
        watchlist_stock_ids = [w['stock_id'] for w in watchlist]
        summary = get_user_portfolio_summary(session['user_id'])
        if summary:
            cash_balance = summary['cash_balance']

    return render_template(
        'market/index.html',
        stocks=stocks,
        sectors=sectors,
        selected_sector=sector,
        sort_by=sort_by,
        search=search,
        watchlist_stock_ids=watchlist_stock_ids,
        cash_balance=cash_balance
    )

@market_bp.route('/market/stock/<int:stock_id>')
def detail(stock_id):
    stock = get_stock_by_id(stock_id)
    if not stock:
        return "Stock Not Found", 404
        
    history = get_stock_price_history(stock_id, limit=30)
    
    in_watchlist = False
    owned_quantity = 0
    cash_balance = 0.0
    
    if 'user_id' in session:
        summary = get_user_portfolio_summary(session['user_id'])
        if summary:
            cash_balance = summary['cash_balance']
            for h in summary['holdings']:
                if h['stock_id'] == stock_id:
                    owned_quantity = h['total_quantity']
                    break
        watchlist = get_user_watchlist(session['user_id'])
        in_watchlist = any(w['stock_id'] == stock_id for w in watchlist)

    return render_template(
        'market/detail.html',
        stock=stock,
        history=history,
        in_watchlist=in_watchlist,
        owned_quantity=owned_quantity,
        cash_balance=cash_balance
    )
