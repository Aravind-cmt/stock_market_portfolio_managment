-- =============================================================================
-- Stock Market Portfolio Management System
-- Comprehensive Sample Data (MySQL 8.0+)
-- =============================================================================

USE stock_portfolio_db;

-- -----------------------------------------------------------------------------
-- 1. Insert Admin
-- Default credentials: admin@stockpulse.com / Admin@123
-- -----------------------------------------------------------------------------
INSERT INTO Admin (admin_id, username, email, password_hash, role)
VALUES (
    1,
    'admin',
    'admin@stockpulse.com',
    'scrypt:32768:8:1$qEohFtSbWikdWp0G$7a1b76313f5f0f4bb92728214331686d4a6c188b37ecc05dd43539b6f9db41b0eee383e6c00d3543a1e9c7bd8d0f36857f60a1d231f9d172206e96300d348f01',
    'SUPER_ADMIN'
);

-- -----------------------------------------------------------------------------
-- 2. Insert 10 Registered Users
-- All users configured with password: Password@123
-- Initial cash balance: ₹1,00,000 to ₹2,50,000 for simulated paper trading.
-- -----------------------------------------------------------------------------
INSERT INTO Users (user_id, name, email, phone, password_hash, cash_balance, account_status, created_at)
VALUES
(1, 'Aravind Sharma', 'aravind@gmail.com', '9876543210', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 145200.00, 'ACTIVE', '2026-01-10 10:00:00'),
(2, 'Priya Nair', 'priya.nair@outlook.com', '9876543211', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 82500.00, 'ACTIVE', '2026-01-12 11:30:00'),
(3, 'Rahul Verma', 'rahul.verma@gmail.com', '9876543212', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 94000.00, 'ACTIVE', '2026-01-15 09:15:00'),
(4, 'Ananya Iyer', 'ananya.iyer@yahoo.com', '9876543213', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 120500.00, 'ACTIVE', '2026-01-18 14:20:00'),
(5, 'Vikram Singh', 'vikram.singh@gmail.com', '9876543214', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 67000.00, 'ACTIVE', '2026-01-20 16:45:00'),
(6, 'Sneha Patel', 'sneha.patel@rediffmail.com', '9876543215', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 115000.00, 'ACTIVE', '2026-01-22 12:10:00'),
(7, 'Rohan Kulkarni', 'rohan.k@gmail.com', '9876543216', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 78900.00, 'ACTIVE', '2026-01-25 15:30:00'),
(8, 'Divya Menon', 'divya.menon@gmail.com', '9876543217', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 135000.00, 'ACTIVE', '2026-01-28 10:40:00'),
(9, 'Karthik Raja', 'karthik.raja@zoho.com', '9876543218', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 99500.00, 'ACTIVE', '2026-02-01 11:00:00'),
(10, 'Neha Gupta', 'neha.gupta@gmail.com', '9876543219', 'scrypt:32768:8:1$Sz98oCqOJ1F5fEvb$ac097edd489549aae61127840427f82bac53d2bde6a9463243b4516604b1dfd9e662c4d37d2e6e96aa9d6ba43a4d189426b5cfa50f5c136b232af0ca54eaa731', 150000.00, 'ACTIVE', '2026-02-05 13:25:00');

-- -----------------------------------------------------------------------------
-- 3. Insert 22 Prominent Indian Stocks (NSE/BSE Listed)
-- Realistic demonstration prices across various economy sectors.
-- -----------------------------------------------------------------------------
INSERT INTO Stocks (stock_id, symbol, company_name, sector, current_price, day_change, day_change_percent, high_52w, low_52w, volume)
VALUES
(1,  'RELIANCE',   'Reliance Industries Limited',         'Energy & Petrochem',   2945.50,  32.40,  1.11,  3024.90, 2220.30, 4820300),
(2,  'TCS',        'Tata Consultancy Services Ltd',       'Information Tech',     4180.25, -15.80, -0.38,  4254.75, 3313.00, 1925400),
(3,  'INFY',       'Infosys Limited',                     'Information Tech',     1865.00,  18.50,  1.00,  1935.00, 1358.35, 6215000),
(4,  'HDFCBANK',   'HDFC Bank Limited',                   'Banking & Finance',    1648.75,   8.20,  0.50,  1794.00, 1363.55, 9840200),
(5,  'ICICIBANK',  'ICICI Bank Limited',                  'Banking & Finance',    1232.10,  14.60,  1.20,  1257.80,  913.00, 7150400),
(6,  'SBIN',       'State Bank of India',                 'Banking & Finance',     815.40,  -4.20, -0.51,   891.55,  555.25, 11450000),
(7,  'BHARTIARTL', 'Bharti Airtel Limited',               'Telecommunications',   1540.00,  22.10,  1.46,  1610.00,  880.00, 3950000),
(8,  'ITC',        'ITC Limited',                         'FMCG',                  492.30,   3.15,  0.64,   514.90,  399.30, 8430000),
(9,  'HINDUNILVR', 'Hindustan Unilever Limited',          'FMCG',                 2725.00, -18.70, -0.68,  3035.00, 2172.05, 1420000),
(10, 'LT',         'Larsen & Toubro Limited',             'Infrastructure',       3620.00,  45.00,  1.26,  3919.90, 2871.10, 2100500),
(11, 'TATAMOTORS', 'Tata Motors Limited',                 'Automobile',            980.50, -12.30, -1.24,  1179.05,  648.00, 7850000),
(12, 'MARUTI',     'Maruti Suzuki India Limited',         'Automobile',          12450.00, 110.00,  0.89, 13680.00, 9737.50,  430200),
(13, 'WIPRO',      'Wipro Limited',                       'Information Tech',      545.60,   2.10,  0.39,   564.00,  375.00, 5120000),
(14, 'SUNPHARMA',  'Sun Pharmaceutical Industries Ltd',   'Healthcare & Pharma',  1790.00,  15.00,  0.84,  1835.00, 1110.00, 1870000),
(15, 'BAJFINANCE', 'Bajaj Finance Limited',               'Financial Services',   7150.00, -85.00, -1.17,  8192.00, 6187.80, 1250000),
(16, 'TITAN',      'Titan Company Limited',               'Consumer Discretionary',3480.00, 25.50,  0.74,  3886.95, 2925.00, 1105000),
(17, 'ADANIENT',   'Adani Enterprises Limited',           'Conglomerate',         2950.00, -35.00, -1.17,  3743.00, 2142.00, 2340000),
(18, 'NTPC',       'NTPC Limited',                        'Power & Utilities',     412.80,   6.40,  1.57,   435.00,  231.25, 8900000),
(19, 'ONGC',       'Oil and Natural Gas Corporation Ltd', 'Energy & Petrochem',    295.20,  -1.80, -0.61,   344.75,  183.00, 9300000),
(20, 'POWERGRID',  'Power Grid Corporation of India Ltd', 'Power & Utilities',     338.50,   4.20,  1.26,   366.25,  200.50, 6700000),
(21, 'KOTAKBANK',  'Kotak Mahindra Bank Limited',         'Banking & Finance',    1785.00,   9.50,  0.54,  1925.00, 1543.85, 3120000),
(22, 'ASIANPAINT', 'Asian Paints Limited',                'Consumer Goods',       2890.00, -22.00, -0.76,  3422.95, 2670.10, 1340000);

-- -----------------------------------------------------------------------------
-- 4. Insert Historical Stock Price Data (For Trend Analysis and Charts)
-- -----------------------------------------------------------------------------
INSERT INTO Stock_Price_History (stock_id, price, recorded_at)
VALUES
-- RELIANCE historical trend
(1, 2820.00, '2026-02-01 15:30:00'),
(1, 2855.50, '2026-02-02 15:30:00'),
(1, 2890.00, '2026-02-03 15:30:00'),
(1, 2910.25, '2026-02-04 15:30:00'),
(1, 2945.50, '2026-02-05 15:30:00'),
-- TCS historical trend
(2, 4120.00, '2026-02-01 15:30:00'),
(2, 4150.50, '2026-02-02 15:30:00'),
(2, 4205.00, '2026-02-03 15:30:00'),
(2, 4196.00, '2026-02-04 15:30:00'),
(2, 4180.25, '2026-02-05 15:30:00'),
-- INFY historical trend
(3, 1810.00, '2026-02-01 15:30:00'),
(3, 1835.00, '2026-02-02 15:30:00'),
(3, 1840.50, '2026-02-03 15:30:00'),
(3, 1850.00, '2026-02-04 15:30:00'),
(3, 1865.00, '2026-02-05 15:30:00'),
-- HDFCBANK historical trend
(4, 1610.00, '2026-02-01 15:30:00'),
(4, 1625.50, '2026-02-02 15:30:00'),
(4, 1640.00, '2026-02-03 15:30:00'),
(4, 1640.50, '2026-02-04 15:30:00'),
(4, 1648.75, '2026-02-05 15:30:00'),
-- ICICIBANK historical trend
(5, 1195.00, '2026-02-01 15:30:00'),
(5, 1208.00, '2026-02-02 15:30:00'),
(5, 1215.50, '2026-02-03 15:30:00'),
(5, 1222.00, '2026-02-04 15:30:00'),
(5, 1232.10, '2026-02-05 15:30:00'),
-- TATAMOTORS historical trend
(11, 950.00, '2026-02-01 15:30:00'),
(11, 968.00, '2026-02-02 15:30:00'),
(11, 985.50, '2026-02-03 15:30:00'),
(11, 992.80, '2026-02-04 15:30:00'),
(11, 980.50, '2026-02-05 15:30:00');

-- -----------------------------------------------------------------------------
-- 5. Insert Realistic BUY and SELL Transactions
-- Demonstrating buy history, averaging, and partial sales.
-- -----------------------------------------------------------------------------
INSERT INTO Transactions (transaction_id, user_id, stock_id, transaction_type, quantity, price, total_amount, transaction_date, transaction_time, transaction_status)
VALUES
-- User 1: Aravind Sharma
(1,  1, 1,  'BUY',  15, 2850.00, 42750.00, '2026-01-15', '10:15:20', 'COMPLETED'),
(2,  1, 3,  'BUY',  25, 1820.00, 45500.00, '2026-01-18', '11:42:10', 'COMPLETED'),
(3,  1, 4,  'BUY',  20, 1620.00, 32400.00, '2026-01-20', '14:05:00', 'COMPLETED'),
(4,  1, 1,  'BUY',   5, 2900.00, 14500.00, '2026-01-28', '09:30:15', 'COMPLETED'),
(5,  1, 3,  'SELL',  5, 1860.00,  9300.00, '2026-02-02', '13:20:45', 'COMPLETED'),

-- User 2: Priya Nair
(6,  2, 2,  'BUY',  10, 4150.00, 41500.00, '2026-01-16', '10:30:00', 'COMPLETED'),
(7,  2, 5,  'BUY',  30, 1210.00, 36300.00, '2026-01-22', '12:15:30', 'COMPLETED'),
(8,  2, 8,  'BUY',  50,  485.00, 24250.00, '2026-01-25', '15:10:00', 'COMPLETED'),
(9,  2, 5,  'SELL', 10, 1235.00, 12350.00, '2026-02-03', '11:05:00', 'COMPLETED'),

-- User 3: Rahul Verma
(10, 3, 6,  'BUY',  60,  805.00, 48300.00, '2026-01-19', '09:45:00', 'COMPLETED'),
(11, 3, 11, 'BUY',  40,  965.00, 38600.00, '2026-01-23', '14:50:20', 'COMPLETED'),
(12, 3, 18, 'BUY',  50,  405.00, 20250.00, '2026-01-30', '10:20:00', 'COMPLETED'),

-- User 4: Ananya Iyer
(13, 4, 7,  'BUY',  25, 1510.00, 37750.00, '2026-01-21', '11:15:00', 'COMPLETED'),
(14, 4, 14, 'BUY',  20, 1750.00, 35000.00, '2026-01-26', '13:40:00', 'COMPLETED'),
(15, 4, 16, 'BUY',  10, 3420.00, 34200.00, '2026-02-01', '15:00:00', 'COMPLETED'),

-- User 5: Vikram Singh
(16, 5, 10, 'BUY',  15, 3580.00, 53700.00, '2026-01-24', '10:00:00', 'COMPLETED'),
(17, 5, 19, 'BUY', 100,  290.00, 29000.00, '2026-01-27', '12:30:00', 'COMPLETED'),
(18, 5, 19, 'SELL', 30,  298.00,  8940.00, '2026-02-04', '14:15:00', 'COMPLETED'),

-- User 6: Sneha Patel
(19, 6, 9,  'BUY',  15, 2690.00, 40350.00, '2026-01-26', '11:00:00', 'COMPLETED'),
(20, 6, 12, 'BUY',   3, 12300.0, 36900.00, '2026-01-29', '14:20:00', 'COMPLETED'),

-- User 7: Rohan Kulkarni
(21, 7, 13, 'BUY',  80,  538.00, 43040.00, '2026-01-28', '10:45:00', 'COMPLETED'),
(22, 7, 20, 'BUY', 100,  330.00, 33000.00, '2026-02-02', '12:00:00', 'COMPLETED');

-- -----------------------------------------------------------------------------
-- 6. Insert Corresponding Portfolio Holdings
-- Derived accurately from the buy & sell transactions above.
-- Average buy price recalculated using weighted average.
-- -----------------------------------------------------------------------------
INSERT INTO Portfolio (portfolio_id, user_id, stock_id, total_quantity, average_buy_price, updated_at)
VALUES
-- User 1 holdings:
-- RELIANCE: 15 @ 2850 + 5 @ 2900 = 20 @ 2862.50
(1, 1, 1, 20, 2862.50, '2026-01-28 09:30:15'),
-- INFY: 25 @ 1820, sold 5 => 20 @ 1820.00
(2, 1, 3, 20, 1820.00, '2026-02-02 13:20:45'),
-- HDFCBANK: 20 @ 1620.00
(3, 1, 4, 20, 1620.00, '2026-01-20 14:05:00'),

-- User 2 holdings:
-- TCS: 10 @ 4150.00
(4, 2, 2, 10, 4150.00, '2026-01-16 10:30:00'),
-- ICICIBANK: 30 @ 1210, sold 10 => 20 @ 1210.00
(5, 2, 5, 20, 1210.00, '2026-02-03 11:05:00'),
-- ITC: 50 @ 485.00
(6, 2, 8, 50,  485.00, '2026-01-25 15:10:00'),

-- User 3 holdings:
-- SBIN: 60 @ 805.00
(7, 3, 6, 60,  805.00, '2026-01-19 09:45:00'),
-- TATAMOTORS: 40 @ 965.00
(8, 3, 11, 40, 965.00, '2026-01-23 14:50:20'),
-- NTPC: 50 @ 405.00
(9, 3, 18, 50, 405.00, '2026-01-30 10:20:00'),

-- User 4 holdings:
-- BHARTIARTL: 25 @ 1510.00
(10, 4, 7, 25, 1510.00, '2026-01-21 11:15:00'),
-- SUNPHARMA: 20 @ 1750.00
(11, 4, 14, 20, 1750.00, '2026-01-26 13:40:00'),
-- TITAN: 10 @ 3420.00
(12, 4, 16, 10, 3420.00, '2026-02-01 15:00:00'),

-- User 5 holdings:
-- LT: 15 @ 3580.00
(13, 5, 10, 15, 3580.00, '2026-01-24 10:00:00'),
-- ONGC: 100 @ 290, sold 30 => 70 @ 290.00
(14, 5, 19, 70,  290.00, '2026-02-04 14:15:00'),

-- User 6 holdings:
-- HINDUNILVR: 15 @ 2690.00
(15, 6, 9, 15, 2690.00, '2026-01-26 11:00:00'),
-- MARUTI: 3 @ 12300.00
(16, 6, 12, 3, 12300.00, '2026-01-29 14:20:00'),

-- User 7 holdings:
-- WIPRO: 80 @ 538.00
(17, 7, 13, 80,  538.00, '2026-01-28 10:45:00'),
-- POWERGRID: 100 @ 330.00
(18, 7, 20, 100, 330.00, '2026-02-02 12:00:00');

-- -----------------------------------------------------------------------------
-- 7. Insert Watchlist Records
-- -----------------------------------------------------------------------------
INSERT INTO Watchlist (watchlist_id, user_id, stock_id, added_at)
VALUES
(1,  1, 2,  '2026-01-12 12:00:00'), -- Aravind watches TCS
(2,  1, 5,  '2026-01-14 15:20:00'), -- Aravind watches ICICIBANK
(3,  1, 11, '2026-01-20 09:40:00'), -- Aravind watches TATAMOTORS
(4,  1, 15, '2026-01-25 14:10:00'), -- Aravind watches BAJFINANCE
(5,  2, 1,  '2026-01-15 11:30:00'), -- Priya watches RELIANCE
(6,  2, 7,  '2026-01-20 16:00:00'), -- Priya watches BHARTIARTL
(7,  3, 3,  '2026-01-18 10:00:00'), -- Rahul watches INFY
(8,  3, 10, '2026-01-22 13:15:00'), -- Rahul watches LT
(9,  4, 1,  '2026-01-19 14:45:00'), -- Ananya watches RELIANCE
(10, 4, 4,  '2026-01-24 16:30:00'), -- Ananya watches HDFCBANK
(11, 5, 2,  '2026-01-21 09:30:00'), -- Vikram watches TCS
(12, 6, 16, '2026-01-27 10:15:00'); -- Sneha watches TITAN

-- -----------------------------------------------------------------------------
-- 8. Insert Audit Logs
-- -----------------------------------------------------------------------------
INSERT INTO Audit_Log (log_id, user_id, action, table_name, record_id, action_timestamp, description)
VALUES
(1,  1, 'BUY_ORDER',  'Transactions', 1,  '2026-01-15 10:15:20', 'User 1 purchased 15 shares of RELIANCE at ₹2850.00'),
(2,  1, 'BUY_ORDER',  'Transactions', 2,  '2026-01-18 11:42:10', 'User 1 purchased 25 shares of INFY at ₹1820.00'),
(3,  1, 'BUY_ORDER',  'Transactions', 3,  '2026-01-20 14:05:00', 'User 1 purchased 20 shares of HDFCBANK at ₹1620.00'),
(4,  1, 'BUY_ORDER',  'Transactions', 4,  '2026-01-28 09:30:15', 'User 1 purchased 5 shares of RELIANCE at ₹2900.00'),
(5,  1, 'SELL_ORDER', 'Transactions', 5,  '2026-02-02 13:20:45', 'User 1 sold 5 shares of INFY at ₹1860.00. Realized profit: ₹200.00'),
(6,  2, 'BUY_ORDER',  'Transactions', 6,  '2026-01-16 10:30:00', 'User 2 purchased 10 shares of TCS at ₹4150.00'),
(7,  2, 'BUY_ORDER',  'Transactions', 7,  '2026-01-22 12:15:30', 'User 2 purchased 30 shares of ICICIBANK at ₹1210.00'),
(8,  2, 'SELL_ORDER', 'Transactions', 9,  '2026-02-03 11:05:00', 'User 2 sold 10 shares of ICICIBANK at ₹1235.00. Realized profit: ₹250.00'),
(9,  NULL, 'PRICE_UPDATE', 'Stocks', 1,    '2026-02-05 15:30:00', 'Market close price updated for RELIANCE to ₹2945.50'),
(10, NULL, 'PRICE_UPDATE', 'Stocks', 2,    '2026-02-05 15:30:00', 'Market close price updated for TCS to ₹4180.25');
