<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/bootstrap.php';
require_once __DIR__ . '/../includes/layout.php';
$user=require_login();
if($user['role']!=='USER')redirect('/admin/dashboard.php');
$search=trim((string)($_GET['search']??''));
$sector=trim((string)($_GET['sector']??''));
$sql='SELECT * FROM Stocks WHERE 1=1'; $params=[];
if($search!==''){$sql.=' AND (symbol LIKE ? OR company_name LIKE ?)';$params=["%$search%","%$search%"];}
if($sector!==''){$sql.=' AND sector=?';$params[]=$sector;}
$sql.=' ORDER BY symbol';
$stmt=db()->prepare($sql);$stmt->execute($params);$stocks=$stmt->fetchAll();
$sectors=db()->query('SELECT DISTINCT sector FROM Stocks ORDER BY sector')->fetchAll();
$body='<form class="card mb-3 d-flex gap-2" method="get"><input class="form-control" name="search" placeholder="Search symbol or company" value="'.e($search).'">'
    .'<select class="form-select" name="sector"><option value="">All sectors</option>';
foreach($sectors as $s){$selected=$sector===($s['sector']??'')?' selected':'';$body.='<option value="'.e($s['sector']).'"'.$selected.'>'.e($s['sector']).'</option>';}
$body.='</select><button class="btn btn-primary">Search</button></form>';
$body.='<div class="table-card"><table class="table table-hover"><thead><tr><th>Symbol</th><th>Company</th><th>Sector</th><th>Price</th><th>Change</th><th></th></tr></thead><tbody>';
foreach($stocks as $stock){$change=(float)$stock['day_change'];$body.='<tr><td><strong>'.e($stock['symbol']).'</strong></td><td>'.e($stock['company_name']).'</td><td>'.e($stock['sector']).'</td><td>₹'.number_format((float)$stock['current_price'],2).'</td><td class="'.($change>=0?'profit':'loss').'">'.number_format($change,2).'</td>'
    .'<td><a class="btn btn-sm btn-primary" href="/user/trade.php?stock_id='.(int)$stock['stock_id'].'&action=buy">Trade</a></td></tr>';}
$body.='</tbody></table></div>';
render_layout('Stock Market',$body,$user);
