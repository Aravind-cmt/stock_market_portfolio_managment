<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';
$super=require_super_admin();if($_SERVER['REQUEST_METHOD']!=='POST'){http_response_code(405);exit('Method not allowed.');}csrf_verify();
$target=(int)($_POST['target_user_id']??0);if($target<=0||$target===($super['user_id']))flash('This account cannot be demoted.','danger');
else{$check=db()->prepare("SELECT u.name,r.role_name,u.account_status FROM Users u JOIN User_Roles ur ON ur.user_id=u.user_id JOIN Roles r ON r.role_id=ur.role_id WHERE u.user_id=?");$check->execute([$target]);$targetUser=$check->fetch();
 if(!$targetUser||$targetUser['role_name']!=='ADMIN')flash('Only an Administrator can be demoted.','danger');
 else{db()->beginTransaction();try{$userRole=db()->query("SELECT role_id FROM Roles WHERE role_name='USER'")->fetch();db()->prepare('DELETE FROM User_Roles WHERE user_id=?')->execute([$target]);db()->prepare('INSERT INTO User_Roles (user_id,role_id,assigned_by,assigned_at) VALUES (?,?,?,CURRENT_TIMESTAMP)')->execute([$target,(int)$userRole['role_id'],$super['user_id']]);db()->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,previous_value,new_value,description) VALUES (?,?,?,?,?,?,?,?)")->execute([$super['user_id'],$target,'ROLE_CHANGE','User_Roles',$target,'ADMIN','USER','Removed Administrator privileges']);db()->commit();flash('Administrator privileges revoked.','success');}catch(Throwable$e){db()->rollBack();flash('Demotion failed.','danger');}}}
redirect('/admin/admins.php');
