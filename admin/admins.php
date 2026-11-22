<?php
declare(strict_types=1);require_once __DIR__.'/../includes/bootstrap.php';require_once __DIR__.'/../includes/layout.php';
$user=require_super_admin();$search=trim((string)($_GET['search']??''));
$sql="SELECT u.user_id,u.name,u.email,u.phone,u.account_status,u.created_at,r.role_name,ur.assigned_at,assigner.name assigned_by_name
 FROM Users u JOIN User_Roles ur ON ur.user_id=u.user_id JOIN Roles r ON r.role_id=ur.role_id
 LEFT JOIN Users assigner ON assigner.user_id=ur.assigned_by";
$params=[];
if($search!==''){$sql.=" WHERE u.name LIKE ? OR u.email LIKE ?";$params=["%$search%","%$search%"];}
$sql.=" ORDER BY CASE r.role_name WHEN 'SUPER_ADMIN' THEN 1 WHEN 'ADMIN' THEN 2 ELSE 3 END,u.name";
$stmt=db()->prepare($sql);$stmt->execute($params);$users=$stmt->fetchAll();
$body='<div class="d-flex justify-content-between mb-3"><form class="d-flex gap-2 flex-grow-1 me-3" method="get"><input class="form-control" name="search" placeholder="Search name or email" value="'.e($search).'"><button class="btn btn-primary">Search</button></form><a class="btn btn-dark" href="/admin/add-admin.php">Add Admin</a></div>';
$body.='<div class="table-card"><table class="table table-hover"><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Assigned At</th><th>Assigned By</th><th></th></tr></thead><tbody>';
foreach($users as$u){$body.='<tr><td>'.(int)$u['user_id'].'</td><td>'.e($u['name']).'</td><td>'.e($u['email']).'</td><td>'.e($u['role_name']).'</td><td>'.e($u['account_status']).'</td><td>'.e((string)$u['assigned_at']).'</td><td>'.e((string)($u['assigned_by_name']??'System')).'</td><td>';
if($u['role_name']==='ADMIN'){$body.='<form method="post" action="/admin/remove-admin.php"><input type="hidden" name="csrf_token" value="'.e(csrf_token()).'"><input type="hidden" name="target_user_id" value="'.(int)$u['user_id'].'"><button class="btn btn-sm btn-outline-danger" data-confirm="Remove Administrator privileges?">Remove Admin</button></form>'; }
$body.='</td></tr>';}$body.='</tbody></table></div>';render_layout('Admin Management',$body,$user,true);
