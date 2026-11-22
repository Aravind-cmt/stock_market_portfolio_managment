<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';
$user=require_login();if($user['role']!=='USER')exit('Access denied.');
$type=$_GET['type']??'transactions';$where='WHERE t.user_id=?';$params=[(int)$user['user_id']];
if($type==='buy')$where.=" AND t.transaction_type='BUY'";
if($type==='sell')$where.=" AND t.transaction_type='SELL'";
$stmt=db()->prepare("SELECT t.transaction_date,t.transaction_type,s.symbol,t.quantity,t.price,t.total_amount,t.transaction_status FROM Transactions t JOIN Stocks s ON s.stock_id=t.stock_id $where ORDER BY t.transaction_id");$stmt->execute($params);
header('Content-Type: text/csv');header('Content-Disposition: attachment; filename="stockpulse_report.csv"');
$out=fopen('php://output','w');fputcsv($out,['Date','Type','Symbol','Quantity','Price','Amount','Status']);
foreach($stmt->fetchAll() as$r)fputcsv($out,$r);fclose($out);
