<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_login();if($user['role']!=='USER')redirect('/admin/dashboard.php');
$stmt=db()->prepare("SELECT t.*,s.symbol,s.company_name FROM Transactions t JOIN Stocks s ON s.stock_id=t.stock_id WHERE t.user_id=? ORDER BY t.transaction_id DESC");$stmt->execute([$user['user_id']]);$transactions=$stmt->fetchAll();
$body='<div class="table-card"><table class="table table-hover"><thead><tr><th>ID</th><th>Date</th><th>Stock</th><th>Type</th><th>Quantity</th><th>Price</th><th>Total</th><th>Status</th></tr></thead><tbody>';
foreach($transactions as $t){$body.='<tr><td>'.(int)$t['transaction_id'].'</td><td>'.e(substr((string)$t['transaction_date'].' '.$t['transaction_time'],0,19)).'</td><td><strong>'.e($t['symbol']).'</strong></td><td>'.e($t['transaction_type']).'</td><td>'.(int)$t['quantity'].'</td><td>₹'.number_format((float)$t['price'],2).'</td><td>₹'.number_format((float)$t['total_amount'],2).'</td><td>'.e($t['transaction_status']).'</td></tr>';}
$body.='</tbody></table></div>';render_layout('Transaction History',$body,$user);
