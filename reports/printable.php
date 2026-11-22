<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';
require_once __DIR__.'/../includes/layout.php';
$user=require_login();
if($user['role']!=='USER') redirect('/admin/dashboard.php');
$type=$_GET['type']??'transactions';
$where='WHERE t.user_id=?';$params=[$user['user_id']];
if($type==='buy')$where.=" AND t.transaction_type='BUY'";
if($type==='sell')$where.=" AND t.transaction_type='SELL'";
$stmt=db()->prepare("SELECT t.*,s.symbol,s.company_name FROM Transactions t JOIN Stocks s ON s.stock_id=t.stock_id $where ORDER BY t.transaction_id DESC");
$stmt->execute($params);$rows=$stmt->fetchAll();
$body='<div class="no-print mb-3"><button class="btn btn-dark" type="button" onclick="window.print()">Print</button></div>';
$body.='<div class="table-card"><table class="table"><thead><tr><th>Date</th><th>Stock</th><th>Type</th><th>Quantity</th><th>Price</th><th>Amount</th></tr></thead><tbody>';
foreach($rows as$row){$body.='<tr><td>'.e((string)$row['transaction_date']).'</td><td>'.e($row['symbol']).'</td><td>'.e($row['transaction_type']).'</td><td>'.(int)$row['quantity'].'</td><td>₹'.number_format((float)$row['price'],2).'</td><td>₹'.number_format((float)$row['total_amount'],2).'</td></tr>';}
$body.='</tbody></table></div>';
render_layout('Printable Report',$body,$user);
