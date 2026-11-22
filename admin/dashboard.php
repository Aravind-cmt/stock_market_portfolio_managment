<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_admin();
$metrics=[
'users'=>(int)db()->query('SELECT COUNT(*) FROM Users')->fetchColumn(),
'stocks'=>(int)db()->query('SELECT COUNT(*) FROM Stocks')->fetchColumn(),
'transactions'=>(int)db()->query('SELECT COUNT(*) FROM Transactions')->fetchColumn(),
'admins'=>(int)db()->query("SELECT COUNT(*) FROM User_Roles ur JOIN Roles r ON r.role_id=ur.role_id WHERE r.role_name IN ('ADMIN','SUPER_ADMIN')")->fetchColumn()];
$body='<div class="card-grid"><div class="card"><small>Registered Users</small><div class="card-value">'.number_format($metrics['users']).'</div></div><div class="card"><small>Stocks</small><div class="card-value">'.number_format($metrics['stocks']).'</div></div><div class="card"><small>Transactions</small><div class="card-value">'.number_format($metrics['transactions']).'</div></div><div class="card"><small>Administrators</small><div class="card-value">'.number_format($metrics['admins']).'</div></div></div>';
render_layout('Administration Dashboard',$body,$user,true);
