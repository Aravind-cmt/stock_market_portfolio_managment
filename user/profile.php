<?php
declare(strict_types=1);
require_once __DIR__.'/../includes/bootstrap.php';
require_once __DIR__.'/../includes/layout.php';
$user=require_login();
if($user['role']!=='USER') redirect('/admin/dashboard.php');

if($_SERVER['REQUEST_METHOD']==='POST'){
    csrf_verify();
    $action=$_POST['action']??'profile';
    if($action==='profile'){
        $name=trim((string)($_POST['name']??''));
        $phone=trim((string)($_POST['phone']??''));
        if($name===''||$phone==='') flash('Name and phone are required.','danger');
        else{
            db()->prepare('UPDATE Users SET name=?,phone=? WHERE user_id=?')->execute([$name,$phone,(int)$user['user_id']]);
            flash('Profile details updated.','success');
            $user['name']=$name;$user['phone']=$phone;
        }
    }elseif($action==='password'){
        $current=(string)($_POST['current_password']??'');
        $new=(string)($_POST['new_password']??'');
        $confirm=(string)($_POST['confirm_password']??'');
        $stored=db()->prepare('SELECT password_hash FROM Users WHERE user_id=?');$stored->execute([$user['user_id']]);$row=$stored->fetch();
        if(!$row||!password_verify($current,(string)$row['password_hash'])) flash('Current password is incorrect.','danger');
        elseif(strlen($new)<8||$new!==$confirm) flash('Use matching passwords of at least 8 characters.','danger');
        else{
            db()->prepare('UPDATE Users SET password_hash=? WHERE user_id=?')->execute([password_hash($new,PASSWORD_DEFAULT),(int)$user['user_id']]);
            flash('Password updated.','success');
        }
    }
}

$body='<div class="dashboard-grid"><form class="card" method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="action" value="profile"><h2 class="h5 mb-3">Profile Details</h2><div class="mb-3"><label class="form-label">Full name</label><input class="form-control" name="name" value="'.e($user['name']).'" required></div><div class="mb-3"><label class="form-label">Email address</label><input class="form-control" value="'.e($user['email']).'" disabled></div><div class="mb-3"><label class="form-label">Phone</label><input class="form-control" name="phone" value="'.e($user['phone']).'" required></div><button class="btn btn-primary">Save Changes</button></form>'
    .'<form class="card" method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="action" value="password"><h2 class="h5 mb-3">Change Password</h2><div class="mb-3"><label class="form-label">Current password</label><input class="form-control" name="current_password" type="password" required></div><div class="mb-3"><label class="form-label">New password</label><input class="form-control" name="new_password" type="password" minlength="8" required></div><div class="mb-3"><label class="form-label">Confirm password</label><input class="form-control" name="confirm_password" type="password" minlength="8" required></div><button class="btn btn-dark">Update Password</button></form></div>';
render_layout('Profile',$body,$user);
