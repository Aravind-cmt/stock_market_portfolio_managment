import os
import sys
import io

# Fix unicode on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure working directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.db import execute_query, execute_update
from services.auth_service import (
    register_user, authenticate_user, get_user_role,
    generate_password_reset_token, reset_password_with_token
)
from services.trade_service import execute_buy, execute_sell
from services.market_service import get_all_stocks, get_stock_by_symbol, get_stock_by_id
from services.portfolio_service import get_user_portfolio_summary, get_user_watchlist, add_to_watchlist, remove_from_watchlist
from services.admin_service import promote_user_to_admin, demote_admin_to_user, get_admin_metrics
from services.report_service import get_report_data, generate_csv_report

test_results = []

def record_test(test_id, category, description, passed, error_msg=""):
    test_results.append({
        'id': test_id,
        'category': category,
        'description': description,
        'status': 'PASS' if passed else 'FAIL',
        'error': error_msg
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {test_id} - {category}: {description}")
    if not passed and error_msg:
        print(f"       ERROR: {error_msg}")

print("================================================================================")
print("     STOCK MARKET PORTFOLIO MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE       ")
print("================================================================================")

# ----------------------------------------------------------------------
# 1. AUTHENTICATION & RBAC TESTS
# ----------------------------------------------------------------------
try:
    # 1.1 Register unique test user
    reg_email = "tester_comprehensive@stockpulse.com"
    execute_update("DELETE FROM Users WHERE email = %s", (reg_email,))
    
    reg_res = register_user("Comprehensive Tester", reg_email, "9876543299", "SecurePass@123")
    record_test("TC-01", "Authentication", "User Registration with hashed password & role assignment", reg_res['success'], reg_res.get('message', ''))
    test_user_id = reg_res.get('user_id')

    # 1.2 Duplicate registration prevention
    dup_res = register_user("Duplicate Tester", reg_email, "9876543299", "SecurePass@123")
    record_test("TC-02", "Authentication", "Prevent duplicate email registration", not dup_res['success'])

    # 1.3 User Login - Success
    auth_user = authenticate_user(reg_email, "SecurePass@123")
    record_test("TC-03", "Authentication", "Valid credential login authentication", auth_user is not None)

    # 1.4 User Login - Bad Password
    bad_auth = authenticate_user(reg_email, "WrongPassword")
    record_test("TC-04", "Authentication", "Reject invalid password authentication", bad_auth is None)

    # 1.5 Role retrieval for standard user
    role_user = get_user_role(test_user_id)
    record_test("TC-05", "RBAC", "Verify default USER role assigned on registration", role_user == 'USER')

    # 1.6 Verify Super Admin role
    super_admin_user = execute_query("SELECT user_id FROM Users WHERE email = %s", ('superadmin@stockpulse.com',), fetch='one')
    if super_admin_user:
        sa_role = get_user_role(super_admin_user['user_id'])
        record_test("TC-06", "RBAC", "Verify SUPER_ADMIN role recognition", sa_role == 'SUPER_ADMIN')
    else:
        record_test("TC-06", "RBAC", "Verify SUPER_ADMIN role recognition", False, "superadmin user not found")

except Exception as e:
    record_test("TC-AUTH-FATAL", "Authentication", "Unexpected authentication exception", False, str(e))

# ----------------------------------------------------------------------
# 2. MARKET MODULE & FILTERING TESTS
# ----------------------------------------------------------------------
try:
    all_stocks = get_all_stocks()
    record_test("TC-07", "Market Module", "Catalog retrieval of stocks", len(all_stocks) >= 20)

    # Search filter
    search_res = get_all_stocks(search="RELIANCE")
    record_test("TC-08", "Market Module", "Stock search by symbol keyword", len(search_res) >= 1 and search_res[0]['symbol'] == 'RELIANCE')

    # Sector filter — use the actual sector name present in the seeded database
    sector_res = get_all_stocks(sector="Banking & Finance")
    record_test("TC-09", "Market Module", "Stock filtering by sector", len(sector_res) >= 1 and all(s['sector'] == "Banking & Finance" for s in sector_res))

    # Sort filter
    sort_res = get_all_stocks(sort_by="price_desc")
    is_sorted_desc = all(sort_res[i]['current_price'] >= sort_res[i+1]['current_price'] for i in range(len(sort_res)-1))
    record_test("TC-10", "Market Module", "Stock sorting by price descending", is_sorted_desc)

except Exception as e:
    record_test("TC-MKT-FATAL", "Market Module", "Unexpected market exception", False, str(e))

# ----------------------------------------------------------------------
# 3. TRADING & ACID TRANSACTION TESTS
# ----------------------------------------------------------------------
try:
    # Set known initial cash balance
    execute_update("UPDATE Users SET cash_balance = 500000.00 WHERE user_id = %s", (test_user_id,))
    rel = get_stock_by_symbol("RELIANCE")
    rel_id = rel['stock_id']
    rel_price = rel['current_price']

    # 3.1 Execute Buy Order
    buy_qty = 10
    buy_res = execute_buy(test_user_id, rel_id, buy_qty)
    record_test("TC-11", "Trade Engine", "Execute ACID BUY order with cash deduction", buy_res['success'], buy_res.get('message', ''))

    # Verify Portfolio holding
    port_holding = execute_query(
        "SELECT total_quantity, average_buy_price FROM Portfolio WHERE user_id = %s AND stock_id = %s",
        (test_user_id, rel_id),
        fetch='one'
    )
    record_test("TC-12", "Portfolio", "Portfolio record updated with purchased quantity", port_holding is not None and port_holding['total_quantity'] == buy_qty)

    # Verify Cash Balance debit
    u_after_buy = execute_query("SELECT cash_balance FROM Users WHERE user_id = %s", (test_user_id,), fetch='one')
    expected_cash = 500000.00 - (buy_qty * rel_price)
    record_test("TC-13", "Trade Engine", "Cash balance debited accurately after BUY", abs(float(u_after_buy['cash_balance']) - expected_cash) < 0.01)

    # 3.2 Execute Second Buy Order (Weighted Average Price test)
    buy2_res = execute_buy(test_user_id, rel_id, 10)
    port_holding_2 = execute_query(
        "SELECT total_quantity FROM Portfolio WHERE user_id = %s AND stock_id = %s",
        (test_user_id, rel_id),
        fetch='one'
    )
    record_test("TC-14", "Trade Engine", "Subsequent BUY accumulates quantity (20 total)", port_holding_2['total_quantity'] == 20)

    # 3.3 Execute Valid Sell Order
    sell_qty = 5
    sell_res = execute_sell(test_user_id, rel_id, sell_qty)
    record_test("TC-15", "Trade Engine", "Execute ACID SELL order with cash credit", sell_res['success'], sell_res.get('message', ''))

    port_holding_3 = execute_query(
        "SELECT total_quantity FROM Portfolio WHERE user_id = %s AND stock_id = %s",
        (test_user_id, rel_id),
        fetch='one'
    )
    record_test("TC-16", "Portfolio", "Portfolio reduced correctly after SELL (15 remaining)", port_holding_3['total_quantity'] == 15)

    # 3.4 Oversell Prevention (trying to sell 100 shares when owning only 15)
    oversell_res = execute_sell(test_user_id, rel_id, 100)
    record_test("TC-17", "Trade Engine", "Strict oversell prevention (insufficient shares rejected)", not oversell_res['success'])

    # 3.5 Insufficient Funds Prevention (trying to buy 10,000 shares worth crores)
    huge_buy = execute_buy(test_user_id, rel_id, 10000)
    record_test("TC-18", "Trade Engine", "Strict insufficient cash balance rejection", not huge_buy['success'])

    # 3.6 Verify Audit Log entry created for trades
    audit_trades = execute_query(
        "SELECT * FROM Audit_Log WHERE acting_user_id = %s AND action IN ('BUY_ORDER', 'SELL_ORDER')",
        (test_user_id,),
        fetch='all'
    )
    record_test("TC-19", "Audit Engine", "Audit_Log entries generated for BUY and SELL operations", len(audit_trades) >= 3)

except Exception as e:
    record_test("TC-TRADE-FATAL", "Trade Engine", "Unexpected trade exception", False, str(e))

# ----------------------------------------------------------------------
# 4. WATCHLIST OPERATIONS
# ----------------------------------------------------------------------
try:
    tcs = get_stock_by_symbol("TCS")
    tcs_id = tcs['stock_id']

    # Add to watchlist
    w_add = add_to_watchlist(test_user_id, tcs_id)
    record_test("TC-20", "Watchlist", "Add stock to user watchlist", w_add['success'])

    # Prevent duplicate in watchlist
    w_dup = add_to_watchlist(test_user_id, tcs_id)
    record_test("TC-21", "Watchlist", "Prevent duplicate addition to watchlist", not w_dup['success'])

    # Fetch watchlist
    w_list = get_user_watchlist(test_user_id)
    record_test("TC-22", "Watchlist", "Retrieve user watchlist items", len(w_list) >= 1)

    # Remove from watchlist
    w_rem = remove_from_watchlist(test_user_id, tcs_id)
    record_test("TC-23", "Watchlist", "Remove stock from user watchlist", w_rem['success'])

except Exception as e:
    record_test("TC-WATCH-FATAL", "Watchlist", "Unexpected watchlist exception", False, str(e))

# ----------------------------------------------------------------------
# 5. ADMIN MANAGEMENT & ROLE TRANSITIONS
# ----------------------------------------------------------------------
try:
    sa_id = super_admin_user['user_id']

    # 5.1 Promote standard user to Admin
    prom_res = promote_user_to_admin(sa_id, test_user_id)
    record_test("TC-24", "Super Admin", "Promote standard user to ADMIN role", prom_res['success'], prom_res.get('message', ''))
    prom_role = get_user_role(test_user_id)
    record_test("TC-25", "RBAC", "Verify user role changed to ADMIN", prom_role == 'ADMIN')

    # 5.2 Demote Admin back to standard User
    dem_res = demote_admin_to_user(sa_id, test_user_id)
    record_test("TC-26", "Super Admin", "Demote ADMIN back to standard USER", dem_res['success'], dem_res.get('message', ''))
    dem_role = get_user_role(test_user_id)
    record_test("TC-27", "RBAC", "Verify user role reverted to USER", dem_role == 'USER')

    # 5.3 Prevent demoting last Super Admin
    dem_sa = demote_admin_to_user(sa_id, sa_id)
    record_test("TC-28", "Super Admin", "Strict protection against demoting last SUPER_ADMIN", not dem_sa['success'])

    # 5.4 Verify Admin metrics
    admin_metrics = get_admin_metrics()
    record_test("TC-29", "Admin Dashboard", "Calculate system-wide admin metrics (users, stocks, volume)", admin_metrics['total_users'] > 0 and admin_metrics['total_stocks'] > 0)

except Exception as e:
    record_test("TC-ADMIN-FATAL", "Super Admin", "Unexpected admin management exception", False, str(e))

# ----------------------------------------------------------------------
# 6. FINANCIAL REPORTING & CSV EXPORT
# ----------------------------------------------------------------------
try:
    report_types = [
        ('all_transactions', 'All Transactions Report'),
        ('buy_transactions', 'BUY Orders Report'),
        ('sell_transactions', 'SELL Orders Report'),
        ('portfolio_holdings', 'Portfolio Holdings Report'),
        ('profit_loss', 'Profit and Loss Summary Report'),
        ('stock_wise_investment', 'Stock-Wise Investment Report')
    ]

    for idx, (rtype, rname) in enumerate(report_types, start=30):
        rep = get_report_data(test_user_id, rtype)
        record_test(f"TC-{idx}", "Financial Reports", f"Generate {rname}", rep is not None and 'records' in rep)

    # CSV Generation Test
    csv_str = generate_csv_report(test_user_id, 'all_transactions')
    record_test("TC-36", "CSV Export", "Stream formatted CSV data with correct column headers", len(csv_str) > 0 and "Transaction ID" in csv_str)

except Exception as e:
    record_test("TC-REP-FATAL", "Financial Reports", "Unexpected report exception", False, str(e))

# ----------------------------------------------------------------------
# CLEANUP & SUMMARY
# ----------------------------------------------------------------------
execute_update("DELETE FROM Portfolio WHERE user_id = %s", (test_user_id,))
execute_update("DELETE FROM Transactions WHERE user_id = %s", (test_user_id,))
execute_update("DELETE FROM Watchlist WHERE user_id = %s", (test_user_id,))
execute_update("DELETE FROM User_Roles WHERE user_id = %s", (test_user_id,))
execute_update("DELETE FROM Audit_Log WHERE acting_user_id = %s OR affected_user_id = %s", (test_user_id, test_user_id))
execute_update("DELETE FROM Users WHERE user_id = %s", (test_user_id,))

passed_count = sum(1 for t in test_results if t['status'] == 'PASS')
failed_count = sum(1 for t in test_results if t['status'] == 'FAIL')
total_count = len(test_results)

print("================================================================================")
print(f"TEST EXECUTION SUMMARY: {passed_count}/{total_count} PASSED ({failed_count} FAILED)")
print("================================================================================")

if failed_count > 0:
    print("FAILED TESTS:")
    for t in test_results:
        if t['status'] == 'FAIL':
            print(f"  - {t['id']}: {t['description']} -> {t['error']}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED SUCCESSFULLY.")
    sys.exit(0)
