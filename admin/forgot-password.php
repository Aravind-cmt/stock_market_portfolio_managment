<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
if($_SERVER['REQUEST_METHOD']==='POST'){csrf_verify();flash('Administrator password recovery is handled through the secure account recovery process.','info');}
$body='<div class="auth-page"><div class="auth-card"><h1>Administrator Password Recovery</h1><form method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><div class="mb-3"><label class="form-label">Email address</label><input class="form-control" name="email" type="email" required></div><button class="btn btn-dark w-100">Continue</button></form></div></div>';render_layout('Administrator Recovery',$body);
