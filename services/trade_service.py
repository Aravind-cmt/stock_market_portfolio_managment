from datetime import date, datetime
from services.db import TransactionScope, get_db_mode, execute_query

def execute_buy(user_id, stock_id, quantity):
    """
    Executes a BUY order with ACID transaction guarantees.
    Calculates weighted average buy price and updates user cash balance and portfolio.
    """
    quantity = int(quantity)
    if quantity <= 0:
        return {'success': False, 'message': 'Quantity must be at least 1 share.'}

    with TransactionScope() as tx:
        # 1. Lock and verify User
        user = tx.execute(
            "SELECT user_id, name, cash_balance, account_status FROM Users WHERE user_id = %s FOR UPDATE",
            (user_id,)
        ).fetchone()

        if not user:
            return {'success': False, 'message': 'User profile not found.'}
        if user['account_status'] != 'ACTIVE':
            return {'success': False, 'message': 'User account is not active.'}

        # 2. Lock and verify Stock
        stock = tx.execute(
            "SELECT stock_id, symbol, current_price FROM Stocks WHERE stock_id = %s",
            (stock_id,)
        ).fetchone()

        if not stock:
            return {'success': False, 'message': 'Selected stock was not found.'}

        price = float(stock['current_price'])
        total_amount = round(price * quantity, 2)
        cash_balance = float(user['cash_balance'])

        if cash_balance < total_amount:
            return {
                'success': False,
                'message': f"Insufficient funds. Required: ₹{total_amount:,.2f}, Available: ₹{cash_balance:,.2f}."
            }

        # 3. Deduct User cash
        tx.execute(
            "UPDATE Users SET cash_balance = cash_balance - %s WHERE user_id = %s",
            (total_amount, user_id)
        )

        # 4. Insert Transaction record
        today = date.today().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')
        tx.execute("""
            INSERT INTO Transactions (
                user_id, stock_id, transaction_type, quantity, price, total_amount, 
                transaction_date, transaction_time, transaction_status
            ) VALUES (%s, %s, 'BUY', %s, %s, %s, %s, %s, 'COMPLETED')
        """, (user_id, stock_id, quantity, price, total_amount, today, now_time))
        tx_id = tx.lastrowid()

        # 5. Update or Insert Portfolio
        portfolio_row = tx.execute(
            "SELECT portfolio_id, total_quantity, average_buy_price FROM Portfolio WHERE user_id = %s AND stock_id = %s FOR UPDATE",
            (user_id, stock_id)
        ).fetchone()

        if portfolio_row and portfolio_row['total_quantity'] > 0:
            old_qty = portfolio_row['total_quantity']
            old_avg = float(portfolio_row['average_buy_price'])
            new_qty = old_qty + quantity
            new_avg = round(((old_qty * old_avg) + (quantity * price)) / new_qty, 2)

            tx.execute("""
                UPDATE Portfolio 
                SET total_quantity = %s, average_buy_price = %s, updated_at = CURRENT_TIMESTAMP
                WHERE portfolio_id = %s
            """, (new_qty, new_avg, portfolio_row['portfolio_id']))
        else:
            tx.execute("""
                INSERT INTO Portfolio (user_id, stock_id, total_quantity, average_buy_price)
                VALUES (%s, %s, %s, %s)
            """, (user_id, stock_id, quantity, price))

        # 6. Audit Log
        tx.execute("""
            INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
            VALUES (%s, 'BUY_ORDER', 'Transactions', %s, %s)
        """, (user_id, tx_id, f"Purchased {quantity} shares of {stock['symbol']} at ₹{price:,.2f} (Total: ₹{total_amount:,.2f})"))

        return {
            'success': True,
            'message': f"Order Executed: Bought {quantity} shares of {stock['symbol']} at ₹{price:,.2f}!",
            'total_amount': total_amount,
            'remaining_cash': cash_balance - total_amount
        }

def execute_sell(user_id, stock_id, quantity):
    """
    Executes a SELL order with ACID transaction guarantees.
    Validates ownership, computes realized P&L, credits cash, and updates portfolio.
    """
    quantity = int(quantity)
    if quantity <= 0:
        return {'success': False, 'message': 'Quantity must be at least 1 share.'}

    with TransactionScope() as tx:
        # 1. Verify User
        user = tx.execute(
            "SELECT user_id, name, cash_balance, account_status FROM Users WHERE user_id = %s",
            (user_id,)
        ).fetchone()

        if not user or user['account_status'] != 'ACTIVE':
            return {'success': False, 'message': 'User account is invalid or inactive.'}

        # 2. Lock and verify Portfolio
        portfolio_row = tx.execute(
            "SELECT portfolio_id, total_quantity, average_buy_price FROM Portfolio WHERE user_id = %s AND stock_id = %s FOR UPDATE",
            (user_id, stock_id)
        ).fetchone()

        if not portfolio_row or portfolio_row['total_quantity'] < quantity:
            held = portfolio_row['total_quantity'] if portfolio_row else 0
            return {
                'success': False,
                'message': f"Oversell prevented. You own {held} shares, cannot sell {quantity} shares."
            }

        # 3. Get Stock info
        stock = tx.execute(
            "SELECT stock_id, symbol, current_price FROM Stocks WHERE stock_id = %s",
            (stock_id,)
        ).fetchone()

        if not stock:
            return {'success': False, 'message': 'Stock not found.'}

        current_qty = portfolio_row['total_quantity']
        avg_buy_price = float(portfolio_row['average_buy_price'])
        sell_price = float(stock['current_price'])
        total_revenue = round(sell_price * quantity, 2)
        realized_pnl = round((sell_price - avg_buy_price) * quantity, 2)

        # 4. Credit cash to user balance
        tx.execute(
            "UPDATE Users SET cash_balance = cash_balance + %s WHERE user_id = %s",
            (total_revenue, user_id)
        )

        # 5. Insert SELL Transaction
        today = date.today().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')
        tx.execute("""
            INSERT INTO Transactions (
                user_id, stock_id, transaction_type, quantity, price, total_amount, 
                transaction_date, transaction_time, transaction_status
            ) VALUES (%s, %s, 'SELL', %s, %s, %s, %s, %s, 'COMPLETED')
        """, (user_id, stock_id, quantity, sell_price, total_revenue, today, now_time))
        tx_id = tx.lastrowid()

        # 6. Update Portfolio
        if current_qty == quantity:
            tx.execute("DELETE FROM Portfolio WHERE portfolio_id = %s", (portfolio_row['portfolio_id'],))
        else:
            tx.execute(
                "UPDATE Portfolio SET total_quantity = total_quantity - %s, updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = %s",
                (quantity, portfolio_row['portfolio_id'])
            )

        # 7. Audit Log
        tx.execute("""
            INSERT INTO Audit_Log (user_id, action, table_name, record_id, description)
            VALUES (%s, 'SELL_ORDER', 'Transactions', %s, %s)
        """, (
            user_id, 
            tx_id, 
            f"Sold {quantity} shares of {stock['symbol']} at ₹{sell_price:,.2f}. Realized P&L: ₹{realized_pnl:,.2f}"
        ))

        return {
            'success': True,
            'message': f"Order Executed: Sold {quantity} shares of {stock['symbol']} at ₹{sell_price:,.2f}!",
            'total_revenue': total_revenue,
            'realized_pnl': realized_pnl
        }
