<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_login();if($user['role']!=='USER')redirect('/admin/dashboard.php');
if($_SERVER['REQUEST_METHOD']==='POST'){csrf_verify();$stockId=(int)($_POST['stock_id']??0);$action=$_POST['action']??'';
    if($action==='add'){try{db()->prepare("INSERT INTO Watchlist (user_id,stock_id) VALUES (?,?)")->execute([$user['user_id'],$stockId]);flash('Stock added to watchlist.','success');}catch(Throwable $e){flash('Stock is already in the watchlist.','info');}}
    if($action==='remove'){db()->prepare("DELETE FROM Watchlist WHERE user_id=? AND stock_id=?")->execute([$user['user_id'],$stockId]);flash('Stock removed from watchlist.','info');}
}
$stmt=db()->prepare("SELECT w.watchlist_id,s.* FROM Watchlist w JOIN Stocks s ON s.stock_id=w.stock_id WHERE w.user_id=? ORDER BY w.added_at DESC");$stmt->execute([$user['user_id']]);$watch=$stmt->fetchAll();
$body='<div class="table-card"><table class="table table-hover"><thead><tr><th>Symbol</th><th>Company</th><th>Price</th><th></th></tr></thead><tbody>';
foreach($watch as $stock){$body.='<tr><td><strong>'.e($stock['symbol']).'</strong></td><td>'.e($stock['company_name']).'</td><td>₹'.number_format((float)$stock['current_price'],2).'</td><td><form method="post" class="d-inline"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="stock_id" value="'.(int)$stock['stock_id'].'"><input type="hidden" name="action" value="remove"><button class="btn btn-sm btn-outline-danger" data-confirm="Remove this stock?">Remove</button></form></td></tr>';}
$body.='</tbody></table></div><h2 class="h5 mt-4">Add Stock</h2><form class="card d-flex gap-2" method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="action" value="add"><select class="form-select" name="stock_id">';
foreach(db()->query("SELECT stock_id,symbol,company_name FROM Stocks ORDER BY symbol")->fetchAll() as $stock){$body.='<option value="'.(int)$stock['stock_id'].'">'.e($stock['symbol'].' - '.$stock['company_name']).'</option>';}
$body.='</select><button class="btn btn-primary">Add</button></form>';render_layout('Watchlist',$body,$user);
