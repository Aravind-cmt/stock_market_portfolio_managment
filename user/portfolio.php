<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_login();if($user['role']!=='USER')redirect('/admin/dashboard.php');
$stmt=db()->prepare("SELECT p.*,s.symbol,s.company_name,s.current_price,ROUND(p.total_quantity*p.average_buy_price,2) invested,ROUND(p.total_quantity*s.current_price,2) value,ROUND(p.total_quantity*s.current_price-p.total_quantity*p.average_buy_price,2) pnl FROM Portfolio p JOIN Stocks s ON s.stock_id=p.stock_id WHERE p.user_id=? AND p.total_quantity>0");
$stmt->execute([$user['user_id']]);$holdings=$stmt->fetchAll();
$body='<div class="table-card"><table class="table table-hover"><thead><tr><th>Stock</th><th>Quantity</th><th>Average Cost</th><th>Invested</th><th>Current Value</th><th>P&amp;L</th></tr></thead><tbody>';
foreach($holdings as $h){$body.='<tr><td><strong>'.e($h['symbol']).'</strong><div class="small text-secondary">'.e($h['company_name']).'</div></td><td>'.(int)$h['total_quantity'].'</td><td>₹'.number_format((float)$h['average_buy_price'],2).'</td><td>₹'.number_format((float)$h['invested'],2).'</td><td>₹'.number_format((float)$h['value'],2).'</td><td class="'.((float)$h['pnl']>=0?'profit':'loss').'">₹'.number_format((float)$h['pnl'],2).'</td></tr>';}
$body.='</tbody></table></div>';render_layout('Portfolio',$body,$user);
