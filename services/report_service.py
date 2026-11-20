import csv
import io
from services.db import execute_query
from services.portfolio_service import get_user_portfolio, get_user_portfolio_summary, get_user_transactions

def get_report_data(user_id, report_type='all_transactions', start_date=None, end_date=None):
    """
    Fetches filtered data based on report type:
    - 'all_transactions': complete transactions
    - 'buy_transactions': buy orders only
    - 'sell_transactions': sell orders only
    - 'portfolio_holdings': current portfolio holdings
    - 'profit_loss': realized & unrealized P&L breakdown
    """
    if report_type == 'all_transactions':
        records = get_user_transactions(user_id, tx_type='ALL', start_date=start_date, end_date=end_date)
        title = "Complete Transaction Report"
    elif report_type == 'buy_transactions':
        records = get_user_transactions(user_id, tx_type='BUY', start_date=start_date, end_date=end_date)
        title = "Buy Transactions Report"
    elif report_type == 'sell_transactions':
        records = get_user_transactions(user_id, tx_type='SELL', start_date=start_date, end_date=end_date)
        title = "Sell Transactions Report"
    elif report_type == 'portfolio_holdings':
        records = get_user_portfolio(user_id)
        title = "Portfolio Holdings Report"
    elif report_type == 'profit_loss':
        records = get_user_portfolio(user_id)
        title = "Profit and Loss Summary Report"
    else:
        records = []
        title = "Custom Report"

    summary = get_user_portfolio_summary(user_id)
    return {
        'title': title,
        'report_type': report_type,
        'records': records,
        'summary': summary,
        'count': len(records)
    }

def generate_csv_report(user_id, report_type='all_transactions', start_date=None, end_date=None):
    """
    Generates CSV string content for download.
    """
    report = get_report_data(user_id, report_type, start_date, end_date)
    records = report['records']
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type in ('all_transactions', 'buy_transactions', 'sell_transactions'):
        # Header
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
        writer.writerow(['Symbol', 'Company Name', 'Sector', 'Quantity', 'Avg Buy Price (INR)', 'Current Price (INR)', 'Total Investment (INR)', 'Current Value (INR)', 'Profit/Loss (INR)', 'P/L (%)'])
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

    return output.getvalue()
