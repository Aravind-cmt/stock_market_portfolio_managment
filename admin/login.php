<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
if(!empty($_SESSION['user_id'])){if(in_array(current_role((int)$_SESSION['user_id']),['ADMIN','SUPER_ADMIN'],true))redirect('/admin/dashboard.php');}
if($_SERVER['REQUEST_METHOD']==='POST'){
 csrf_verify();$email=strtolower(trim((string)($_POST['email']??'')));$password=(string)($_POST['password']??'');
 $stmt=db()->prepare('SELECT * FROM Users WHERE email=?');$stmt->execute([$email]);$user=$stmt->fetch();
 if(!$user||!password_verify($password,(string)$user['password_hash']))flash('Invalid email address or password.','danger');
 else{$role=current_role((int)$user['user_id']);if(!in_array($role,['ADMIN','SUPER_ADMIN'],true))flash('Access denied. This login is for administrators only.','danger');
 elseif($user['account_status']!=='ACTIVE')flash('The administrator account is not active.','danger');
 else{session_regenerate_id(true);$_SESSION['user_id']=$user['user_id'];$_SESSION['user_role']=$role;db()->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,description) VALUES (?,?, 'ADMIN_LOGIN','Users',?,?)")->execute([$user['user_id'],$user['user_id'],$user['user_id'],'Administrator signed in']);redirect('/admin/dashboard.php');}}
}
$body='<div class="auth-page"><div class="auth-card"><h1>Administrator Login</h1><p class="subtitle">Authorized personnel only</p>'
 .'<form method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><div class="mb-3"><label class="form-label">Email address</label><input class="form-control" name="email" type="email" required></div>'
 .'<div class="mb-3"><label class="form-label">Password</label><input class="form-control" name="password" type="password" required></div><button class="btn btn-dark w-100">Sign In</button></form>'
 .'<div class="text-center mt-3"><a href="/admin/forgot-password.php">Forgot password</a></div></div></div>';
render_layout('Administrator Login',$body);
