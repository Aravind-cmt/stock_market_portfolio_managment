import csv
import io
from services.db import execute_query
from services.portfolio_service import get_user_portfolio, get_user_portfolio_summary, get_user_transactions

def get_report_data(user_id, report_type='all_transactions', start_date=None, end_date=None, stock_id=None):
    """
    Fetches filtered data based on report type:
    1. 'all_transactions': complete transaction report
    2. 'buy_transactions': BUY transactions report
    3. 'sell_transactions': SELL transactions report
    4. 'portfolio_holdings': portfolio holdings report
    5. 'profit_loss': profit and loss report
    6. 'stock_wise_investment': stock-wise investment report
    """
    summary = get_user_portfolio_summary(user_id)
    
    if report_type == 'all_transactions':
        records = get_user_transactions(user_id, stock_id=stock_id, tx_type='ALL', start_date=start_date, end_date=end_date)
        title = "Complete Transaction Report"
    elif report_type == 'buy_transactions':
        records = get_user_transactions(user_id, stock_id=stock_id, tx_type='BUY', start_date=start_date, end_date=end_date)
        title = "BUY Transactions Report"
    elif report_type == 'sell_transactions':
        records = get_user_transactions(user_id, stock_id=stock_id, tx_type='SELL', start_date=start_date, end_date=end_date)
        title = "SELL Transactions Report"
    elif report_type == 'portfolio_holdings':
        all_holdings = get_user_portfolio(user_id)
        records = [h for h in all_holdings if not stock_id or h['stock_id'] == stock_id]
        title = "Portfolio Holdings Report"
    elif report_type == 'profit_loss':
        all_holdings = get_user_portfolio(user_id)
        records = [h for h in all_holdings if not stock_id or h['stock_id'] == stock_id]
        title = "Profit and Loss Report"
    elif report_type == 'stock_wise_investment':
        query = """
        SELECT 
            s.stock_id,
            s.symbol,
            s.company_name,
            s.sector,
            s.current_price,
            p.total_quantity,
            p.average_buy_price,
            ROUND(p.total_quantity * p.average_buy_price, 2) AS total_investment,
            ROUND(p.total_quantity * s.current_price, 2) AS current_value,
            ROUND((p.total_quantity * s.current_price) - (p.total_quantity * p.average_buy_price), 2) AS unrealized_pnl,
            ROUND(
                CASE 
                    WHEN p.average_buy_price > 0 THEN 
                        (((s.current_price - p.average_buy_price) / p.average_buy_price) * 100)
                    ELSE 0.00 
                END, 2
            ) AS return_percentage
        FROM Portfolio p
        JOIN Stocks s ON p.stock_id = s.stock_id
        WHERE p.user_id = %s AND p.total_quantity > 0
        """
        params = [user_id]
        if stock_id:
            query += " AND s.stock_id = %s"
            params.append(stock_id)
        query += " ORDER BY total_investment DESC"
        records = execute_query(query, params, fetch='all')
        title = "Stock-Wise Investment Report"
    else:
        records = []
        title = "Custom Report"

    return {
        'title': title,
        'report_type': report_type,
        'records': records,
        'summary': summary,
        'count': len(records)
    }

def generate_csv_report(user_id, report_type='all_transactions', start_date=None, end_date=None, stock_id=None):
    """
    Generates CSV string content for download.
    """
    report = get_report_data(user_id, report_type, start_date, end_date, stock_id)
    records = report['records']
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type in ('all_transactions', 'buy_transactions', 'sell_transactions'):
        writer.writerow(['Transaction ID', 'Date', 'Time', 'Symbol', 'Company Name', 'Type', 'Quantity', 'Price (INR)', 'Total Amount (INR)', 'Status'])
        for r in records:
            writer.writerow([
                r['transaction_id'],
                r['transaction_date'],
                r['transaction_time'],
                r['symbol'],
                r['company_name'],
                r['transaction_type'],
                r['quantity'],
                r['price'],
                r['total_amount'],
                r['transaction_status']
            ])
    elif report_type in ('portfolio_holdings', 'profit_loss'):
        writer.writerow(['Symbol', 'Company Name', 'Sector', 'Quantity', 'Avg Buy Price (INR)', 'Current Price (INR)', 'Total Investment (INR)', 'Current Value (INR)', 'Profit/Loss (INR)', 'Return (%)'])
        for r in records:
            writer.writerow([
                r['symbol'],
                r['company_name'],
                r['sector'],
                r['total_quantity'],
                r['average_buy_price'],
                r['current_price'],
                r['total_investment'],
                r['current_value'],
                r['profit_loss'],
                r['profit_loss_percent']
            ])
    elif report_type == 'stock_wise_investment':
        writer.writerow(['Symbol', 'Company Name', 'Sector', 'Units Held', 'Avg Cost (INR)', 'Market Price (INR)', 'Total Invested (INR)', 'Current Valuation (INR)', 'Net P&L (INR)', 'Return (%)'])
        for r in records:
            writer.writerow([
                r['symbol'],
                r['company_name'],
                r['sector'],
                r['total_quantity'],
                r['average_buy_price'],
                r['current_price'],
                r['total_investment'],
                r['current_value'],
                r['unrealized_pnl'],
                r['return_percentage']
            ])

    return output.getvalue()
