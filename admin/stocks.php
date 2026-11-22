<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_admin();
if($_SERVER['REQUEST_METHOD']==='POST'){csrf_verify();
 $action=$_POST['action']??'';$stockId=(int)($_POST['stock_id']??0);
 if($action==='add'||$action==='edit'){
  $symbol=strtoupper(trim((string)($_POST['symbol']??'')));$name=trim((string)($_POST['company_name']??''));$sector=trim((string)($_POST['sector']??''));$price=(float)($_POST['current_price']??0);
  if($action==='add')db()->prepare("INSERT INTO Stocks(symbol,company_name,sector,current_price) VALUES(?,?,?,?)")->execute([$symbol,$name,$sector,$price]);
  else db()->prepare("UPDATE Stocks SET company_name=?,sector=?,current_price=? WHERE stock_id=?")->execute([$name,$sector,$price,$stockId]);
  db()->prepare("INSERT INTO Audit_Log (acting_user_id,table_name,record_id,action,description) VALUES (?, 'Stocks', ?, 'STOCK_CHANGE', ?)")->execute([$user['user_id'],$stockId||null,$action==='add'?'Stock added':'Stock updated']);
  flash('Stock record saved.','success');
 }elseif($action==='delete'){db()->prepare("DELETE FROM Stocks WHERE stock_id=?")->execute([$stockId]);flash('Stock removed.','info');}
}
$stocks=db()->query('SELECT * FROM Stocks ORDER BY symbol')->fetchAll();
$body='<div class="card mb-4"><form method="post" class="row g-2"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="action" value="add"><div class="col"><input class="form-control" name="symbol" placeholder="Symbol" required></div><div class="col"><input class="form-control" name="company_name" placeholder="Company" required></div><div class="col"><input class="form-control" name="sector" placeholder="Sector" required></div><div class="col"><input class="form-control" name="current_price" type="number" min=".01" step=".01" placeholder="Price" required></div><div class="col-auto"><button class="btn btn-primary">Add Stock</button></div></form></div>';
$body.='<div class="table-card"><table class="table table-hover"><thead><tr><th>Symbol</th><th>Company</th><th>Sector</th><th>Price</th><th></th></tr></thead><tbody>';
foreach($stocks as$s){$body.='<tr><td><strong>'.e($s['symbol']).'</strong></td><td>'.e($s['company_name']).'</td><td>'.e($s['sector']).'</td><td>₹'.number_format((float)$s['current_price'],2).'</td><td><form method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="action" value="delete"><input type="hidden" name="stock_id" value="'.(int)$s['stock_id'].'"><button class="btn btn-sm btn-outline-danger" data-confirm="Remove this stock?">Remove</button></form></td></tr>';}$body.='</tbody></table></div>';render_layout('Stock Management',$body,$user,true);
