<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/bootstrap.php';
require_once __DIR__ . '/../includes/layout.php';

if (!empty($_SESSION['user_id'])) {
    redirect(current_role((int) $_SESSION['user_id']) === 'USER' ? '/user/dashboard.php' : '/admin/dashboard.php');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $email = strtolower(trim((string) ($_POST['email'] ?? '')));
    $password = (string) ($_POST['password'] ?? '');
    $statement = db()->prepare('SELECT * FROM Users WHERE email = ?');
    $statement->execute([$email]);
    $user = $statement->fetch();
    if (!$user || !password_verify($password, (string) $user['password_hash'])) {
        flash('Invalid email address or password.', 'danger');
    } elseif ($user['account_status'] !== 'ACTIVE') {
        flash('Your account is not active.', 'danger');
    } else {
        $role = current_role((int) $user['user_id']);
        if ($role !== 'USER') {
            flash('Administrator accounts must use the administrator login.', 'warning');
        } else {
            session_regenerate_id(true);
            $_SESSION['user_id'] = (int) $user['user_id'];
            $_SESSION['user_role'] = $role;
            db()->prepare("INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, description) VALUES (?, ?, 'USER_LOGIN', 'Users', ?, ?)")
                ->execute([$user['user_id'], $user['user_id'], $user['user_id'], 'Investor signed in']);
            redirect('/user/dashboard.php');
        }
    }
}

$body = '<div class="auth-page"><div class="auth-card"><h1>Investor Login</h1>'
    . '<p class="subtitle">Sign in to access your portfolio</p>'
    . '<form method="post"><input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '">'
    . '<div class="mb-3"><label class="form-label" for="email">Email address</label><input class="form-control" id="email" name="email" type="email" required></div>'
    . '<div class="mb-3"><label class="form-label" for="password">Password</label><input class="form-control" id="password" name="password" type="password" required></div>'
    . '<button class="btn btn-primary w-100" type="submit">Sign In</button></form>'
    . '<div class="login-actions mt-3"><a href="/user/register.php">Register</a><a href="/user/forgot-password.php">Forgot password</a></div>'
    . '</div></div>';
render_layout('Investor Login', $body);
