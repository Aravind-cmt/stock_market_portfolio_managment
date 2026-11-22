<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/bootstrap.php';
require_once __DIR__ . '/../includes/layout.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $name = trim((string) ($_POST['name'] ?? ''));
    $email = strtolower(trim((string) ($_POST['email'] ?? '')));
    $phone = trim((string) ($_POST['phone'] ?? ''));
    $password = (string) ($_POST['password'] ?? '');
    $confirm = (string) ($_POST['confirm_password'] ?? '');
    if ($name === '' || $email === '' || $phone === '' || strlen($password) < 8 || $password !== $confirm) {
        flash('Complete all fields and use matching passwords of at least 8 characters.', 'danger');
    } else {
        $check = db()->prepare('SELECT user_id FROM Users WHERE email = ?');
        $check->execute([$email]);
        if ($check->fetch()) {
            flash('An account with this email already exists.', 'danger');
        } else {
            $hash = password_hash($password, PASSWORD_DEFAULT);
            db()->beginTransaction();
            try {
                $insert = db()->prepare("INSERT INTO Users (name,email,phone,password_hash,cash_balance,account_status) VALUES (?, ?, ?, ?, 100000.00, 'ACTIVE')");
                $insert->execute([$name, $email, $phone, $hash]);
                $id = (int) db()->lastInsertId();
                db()->prepare('INSERT INTO User_Roles (user_id,role_id,assigned_by,assigned_at) VALUES (?,3,NULL,CURRENT_TIMESTAMP)')
                    ->execute([$id]);
                db()->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,new_value,description) VALUES (?, ?, 'USER_REGISTER', 'Users', ?, 'USER', 'Registered investor account')")
                    ->execute([$id, $id, $id]);
                db()->commit();
                flash('Account created successfully.', 'success');
                redirect('/user/login.php');
            } catch (Throwable $error) {
                db()->rollBack();
                flash('Registration could not be completed.', 'danger');
            }
        }
    }
}

$body = '<div class="auth-page"><div class="auth-card"><h1>Create Investor Account</h1>'
    . '<form method="post"><input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '">'
    . '<div class="mb-3"><label class="form-label">Full name</label><input class="form-control" name="name" required></div>'
    . '<div class="mb-3"><label class="form-label">Email address</label><input class="form-control" name="email" type="email" required></div>'
    . '<div class="mb-3"><label class="form-label">Phone</label><input class="form-control" name="phone" required></div>'
    . '<div class="mb-3"><label class="form-label">Password</label><input class="form-control" name="password" type="password" minlength="8" required></div>'
    . '<div class="mb-3"><label class="form-label">Confirm password</label><input class="form-control" name="confirm_password" type="password" minlength="8" required></div>'
    . '<button class="btn btn-primary w-100" type="submit">Create Account</button></form>'
    . '<div class="text-center mt-3"><a href="/user/login.php">Back to login</a></div></div></div>';
render_layout('Register', $body);
