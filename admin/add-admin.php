<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$super=require_super_admin();$search=trim((string)($_GET['search']??''));
$sql="SELECT u.user_id,u.name,u.email,u.phone,u.account_status,u.created_at,r.role_name FROM Users u JOIN User_Roles ur ON ur.user_id=u.user_id JOIN Roles r ON r.role_id=ur.role_id WHERE r.role_name='USER' AND u.account_status='ACTIVE'";
$params=[];if($search!==''){$sql.=" AND (u.name LIKE ? OR u.email LIKE ?)";$params=["%$search%","%$search%"];}$sql.=" ORDER BY u.name";
$stmt=db()->prepare($sql);$stmt->execute($params);$users=$stmt->fetchAll();
if($_SERVER['REQUEST_METHOD']==='POST'){csrf_verify();$target=(int)($_POST['target_user_id']??0);if($target<=0||$target===($super['user_id'])){flash($target===($super['user_id'])?'Self-promotion is prohibited.':'Select a valid user.','danger');}
else{
 $check=db()->prepare("SELECT u.name,u.email,r.role_name,u.account_status FROM Users u JOIN User_Roles ur ON ur.user_id=u.user_id JOIN Roles r ON r.role_id=ur.role_id WHERE u.user_id=?");
 $check->execute([$target]);$targetUser=$check->fetch();
 if(!$targetUser||$targetUser['role_name']!=='USER'||$targetUser['account_status']!=='ACTIVE')flash('The selected account is not eligible.','danger');
 else{db()->beginTransaction();try{$adminRole=db()->query("SELECT role_id FROM Roles WHERE role_name='ADMIN'")->fetch();db()->prepare('DELETE FROM User_Roles WHERE user_id=?')->execute([$target]);db()->prepare('INSERT INTO User_Roles (user_id,role_id,assigned_by,assigned_at) VALUES (?,?,?,CURRENT_TIMESTAMP)')->execute([$target,(int)$adminRole['role_id'],$super['user_id']]);db()->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,previous_value,new_value,description) VALUES (?,?,?,?,?,?,?,?)")->execute([$super['user_id'],$target,'ROLE_CHANGE','User_Roles',$target,'USER','ADMIN','Promoted '.$targetUser['name'].' to ADMIN']);db()->commit();flash('User promoted to Administrator successfully.','success');redirect('/admin/admins.php');}catch(Throwable$e){db()->rollBack();flash('Administrator promotion failed.','danger');}}
}}
$body='<div class="d-flex justify-content-between mb-3"><h2 class="h5">Eligible Registered Users</h2><a class="btn btn-outline-secondary" href="/admin/admins.php">Back</a></div>';
$body.='<form class="card mb-3 d-flex gap-2" method="get"><input class="form-control" name="search" placeholder="Search name or email" value="'.e($search).'"><button class="btn btn-primary">Search</button></form>';
$body.='<div class="table-card"><table class="table table-hover"><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Status</th><th></th></tr></thead><tbody>';
foreach($users as$u){$body.='<tr><td>'.(int)$u['user_id'].'</td><td>'.e($u['name']).'</td><td>'.e($u['email']).'</td><td>'.e($u['account_status']).'</td><td><form method="post"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="target_user_id" value="'.(int)$u['user_id'].'"><button class="btn btn-sm btn-dark" data-confirm="Promote this user to Administrator?">Promote to Admin</button></form></td></tr>';}$body.='</tbody></table></div>';render_layout('Add Administrator',$body,$super,true);
