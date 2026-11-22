<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/bootstrap.php';
require_once __DIR__ . '/../includes/layout.php';
$user = require_login();
if ($user['role'] !== 'USER') redirect('/admin/dashboard.php');

$holdings = db()->prepare("SELECT p.*, s.symbol, s.company_name, s.current_price,
 ROUND(p.total_quantity*p.average_buy_price,2) invested,
 ROUND(p.total_quantity*s.current_price,2) value,
 ROUND(p.total_quantity*s.current_price-p.total_quantity*p.average_buy_price,2) pnl
 FROM Portfolio p JOIN Stocks s ON s.stock_id=p.stock_id WHERE p.user_id=? AND p.total_quantity>0");
$holdings->execute([$user['user_id']]);
$holdings = $holdings->fetchAll();
$invested = array_sum(array_map(fn($r)=>(float)$r['invested'],$holdings));
$value = array_sum(array_map(fn($r)=>(float)$r['value'],$holdings));
$transactions = db()->prepare('SELECT t.*, s.symbol FROM Transactions t JOIN Stocks s ON s.stock_id=t.stock_id WHERE t.user_id=? ORDER BY t.transaction_id DESC LIMIT 5');
$transactions->execute([$user['user_id']]);
$transactions = $transactions->fetchAll();

$body = '<div class="card-grid">'
    . '<div class="card"><small>Cash Balance</small><div class="card-value">₹'.number_format((float)$user['cash_balance'],2).'</div></div>'
    . '<div class="card"><small>Invested Capital</small><div class="card-value">₹'.number_format($invested,2).'</div></div>'
    . '<div class="card"><small>Portfolio Value</small><div class="card-value">₹'.number_format($value,2).'</div></div>'
    . '<div class="card"><small>Unrealized P&amp;L</small><div class="card-value '.(($value-$invested)>=0?'profit':'loss').'">₹'.number_format($value-$invested,2).'</div></div>'
    . '</div>';
$body .= '<div class="dashboard-grid mt-4"><div class="chart-card"><div class="d-flex justify-content-between mb-3"><h2 class="h6 mb-0">Portfolio Allocation</h2><span class="text-secondary small">Current value</span></div><canvas id="portfolioChart" height="220"></canvas></div>';
$body .= '<div class="chart-card"><div class="d-flex justify-content-between mb-3"><h2 class="h6 mb-0">Recent Transactions</h2><a class="small" href="/user/transactions.php">View all</a></div><div class="recent-transactions">';
foreach ($transactions as $tx) {
    $body .= '<div><span><strong>'.e($tx['symbol']).'</strong><small>'.e((string)$tx['transaction_date'].' '.$tx['transaction_type']).'</small></span><strong>₹'.number_format((float)$tx['total_amount'],2).'</strong></div>';
}
$body .= '</div></div></div>';
$body .= '<div class="table-card mt-4"><div class="p-3 border-bottom"><h2 class="h6 mb-0">Stock Holdings</h2></div><table class="table table-hover align-middle"><thead><tr><th>Stock</th><th>Quantity</th><th>Average Price</th><th>Current Value</th><th>P&amp;L</th></tr></thead><tbody>';
foreach ($holdings as $holding) {
    $body .= '<tr><td><strong>'.e($holding['symbol']).'</strong><div class="text-secondary small">'.e($holding['company_name']).'</div></td>'
        .'<td>'.(int)$holding['total_quantity'].'</td><td>₹'.number_format((float)$holding['average_buy_price'],2).'</td>'
        .'<td>₹'.number_format((float)$holding['value'],2).'</td><td class="'.((float)$holding['pnl']>=0?'profit':'loss').'">₹'.number_format((float)$holding['pnl'],2).'</td></tr>';
}
$body .= '</tbody></table></div>';
$labels = [];
$values = [];
foreach ($holdings as $holding) {
    $labels[] = (string)$holding['symbol'];
    $values[] = (float)$holding['value'];
}
$body .= '<script id="portfolio-data" type="application/json">'.json_encode(['labels'=>$labels,'values'=>$values], JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT).'</script>';
render_layout('Investor Dashboard',$body,$user);
