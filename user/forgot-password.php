<?php
declare(strict_types=1);
require_once __DIR__ . '/../includes/bootstrap.php';
require_once __DIR__ . '/../includes/layout.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    csrf_verify();
    $email = strtolower(trim((string) ($_POST['email'] ?? '')));
    $statement = db()->prepare('SELECT user_id FROM Users WHERE email = ?');
    $statement->execute([$email]);
    $user = $statement->fetch();
    if ($user) {
        $token = bin2hex(random_bytes(32));
        db()->prepare("INSERT INTO Password_Reset (user_id,reset_token_hash,expiry_time,is_used) VALUES (?, ?, DATE_ADD(NOW(), INTERVAL 1 HOUR), 0)")
            ->execute([(int) $user['user_id'], password_hash($token, PASSWORD_DEFAULT)]);
        flash('Password recovery is available using reset token: ' . $token, 'info');
    } else {
        flash('If the account exists, recovery instructions will be available.', 'info');
    }
}

$body = '<div class="auth-page"><div class="auth-card"><h1>Forgot Password</h1>'
    . '<form method="post"><input type="hidden" name="csrf_token" value="' . e(csrf_token()) . '">'
    . '<div class="mb-3"><label class="form-label">Email address</label><input class="form-control" name="email" type="email" required></div>'
    . '<button class="btn btn-primary w-100">Request Recovery</button></form>'
    . '<div class="text-center mt-3"><a href="/user/login.php">Back to login</a></div></div></div>';
render_layout('Forgot Password', $body);
