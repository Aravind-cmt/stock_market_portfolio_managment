<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_login();if($user['role']!=='USER')redirect('/admin/dashboard.php');
$type=$_GET['type']??'transactions';
$where='WHERE t.user_id=?';$params=[$user['user_id']];
if($type==='buy'){$where.=" AND t.transaction_type='BUY'";}
if($type==='sell'){$where.=" AND t.transaction_type='SELL'";}
$stmt=db()->prepare("SELECT t.*,s.symbol,s.company_name FROM Transactions t JOIN Stocks s ON s.stock_id=t.stock_id $where ORDER BY t.transaction_id DESC");$stmt->execute($params);$rows=$stmt->fetchAll();
$body='<div class="card mb-3 d-flex flex-row gap-2"><a class="btn btn-outline-primary" href="?type=transactions">All Transactions</a><a class="btn btn-outline-primary" href="?type=buy">Buy Orders</a><a class="btn btn-outline-primary" href="?type=sell">Sell Orders</a><a class="btn btn-success" href="/reports/export.php?type='.e($type).'">Export CSV</a></div>';
$body.='<div class="table-card"><table class="table table-hover"><thead><tr><th>Date</th><th>Stock</th><th>Type</th><th>Quantity</th><th>Price</th><th>Amount</th></tr></thead><tbody>';
foreach($rows as$r){$body.='<tr><td>'.e((string)$r['transaction_date']).'</td><td>'.e($r['symbol']).'</td><td>'.e($r['transaction_type']).'</td><td>'.(int)$r['quantity'].'</td><td>₹'.number_format((float)$r['price'],2).'</td><td>₹'.number_format((float)$r['total_amount'],2).'</td></tr>';}
$body.='</tbody></table></div>';render_layout('Financial Reports',$body,$user);
