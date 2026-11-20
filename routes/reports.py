from flask import Blueprint, render_template, request, session, Response
from services.auth_service import login_required
from services.report_service import get_report_data, generate_csv_report
from services.market_service import get_all_stocks

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    user_id = session['user_id']
    report_type = request.args.get('type', 'all_transactions')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stock_id = request.args.get('stock_id', type=int)

    report = get_report_data(user_id, report_type, start_date, end_date, stock_id)
    stocks = get_all_stocks()
    
    return render_template(
        'reports/index.html',
        report=report,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        stock_id=stock_id,
        stocks=stocks
    )

@reports_bp.route('/reports/export/csv')
@login_required
def export_csv():
    user_id = session['user_id']
    report_type = request.args.get('type', 'all_transactions')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stock_id = request.args.get('stock_id', type=int)

    csv_content = generate_csv_report(user_id, report_type, start_date, end_date, stock_id)
    filename = f"stockpulse_{report_type}_report.csv"
    
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

@reports_bp.route('/reports/printable')
@login_required
def printable():
    user_id = session['user_id']
    report_type = request.args.get('type', 'all_transactions')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    stock_id = request.args.get('stock_id', type=int)

    report = get_report_data(user_id, report_type, start_date, end_date, stock_id)
    return render_template('reports/printable.html', report=report)
