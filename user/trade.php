<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';require_once __DIR__.'/../includes/trade.php';
$user=require_login();if($user['role']!=='USER')redirect('/admin/dashboard.php');
if($_SERVER['REQUEST_METHOD']==='POST'){
    csrf_verify();$stockId=(int)($_POST['stock_id']??0);$quantity=(int)($_POST['quantity']??0);$action=$_POST['action']??'buy';
    $result=$action==='sell'?execute_sell((int)$user['user_id'],$stockId,$quantity):execute_buy((int)$user['user_id'],$stockId,$quantity);
    flash($result['message'],$result['success']?'success':'danger');
}
$stockId=(int)($_GET['stock_id']??0);
$stocks=db()->query('SELECT * FROM Stocks ORDER BY symbol')->fetchAll();
$selected=null;foreach($stocks as $stock){if($stockId===0||$stockId==(int)$stock['stock_id']){$selected=$stock;break;}}
$action=$_GET['action']??'buy';
$body='<form class="card" method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'">'
    .'<input type="hidden" name="action" value="'.e($action).'"><div class="row g-3">'
    .'<div class="col-md-6"><label class="form-label">Stock</label><select class="form-select" name="stock_id">';
foreach($stocks as $stock){$selectedAttr=$selected&&$selected['stock_id']===$stock['stock_id']?' selected':'';$body.='<option value="'.(int)$stock['stock_id'].'"'.$selectedAttr.'>'.e($stock['symbol'].' - '.$stock['company_name']).' (₹'.number_format((float)$stock['current_price'],2).')</option>';}
$body.='</select></div><div class="col-md-3"><label class="form-label">Quantity</label><input class="form-control" name="quantity" type="number" min="1" value="1" required></div>'
    .'<div class="col-md-3 d-flex align-items-end"><button class="btn '.($action==='sell'?'btn-danger':'btn-primary').' w-100">'.($action==='sell'?'Sell Shares':'Buy Shares').'</button></div></div></form>';
render_layout('Trade',$body,$user);
