<?php
declare(strict_types=1);

require_once __DIR__ . '/../config/database.php';

if (session_status() !== PHP_SESSION_ACTIVE) {
    ini_set('session.cookie_httponly', '1');
    ini_set('session.cookie_samesite', 'Lax');
    ini_set('session.use_strict_mode', '1');
    ini_set('session.cookie_secure', (!empty(getenv('SESSION_COOKIE_SECURE')) ? '1' : '0'));
    session_start();
}

function e(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function csrf_token(): string
{
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function csrf_verify(): void
{
    $token = $_POST['csrf_token'] ?? '';
    if (!is_string($token) || !hash_equals($_SESSION['csrf_token'] ?? '', $token)) {
        http_response_code(403);
        exit('Invalid or missing CSRF token.');
    }
}

function flash(string $message, string $type = 'success'): void
{
    $_SESSION['flash'][] = ['message' => $message, 'type' => $type];
}

function consume_flash(): array
{
    $messages = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $messages;
}

function redirect(string $path): never
{
    header('Location: ' . $path);
    exit;
}

function current_role(int $userId): string
{
    $sql = 'SELECT r.role_name
            FROM User_Roles ur
            JOIN Roles r ON r.role_id = ur.role_id
            WHERE ur.user_id = ?
            ORDER BY CASE r.role_name WHEN \'SUPER_ADMIN\' THEN 1 WHEN \'ADMIN\' THEN 2 ELSE 3 END
            LIMIT 1';
    $statement = db()->prepare($sql);
    $statement->execute([$userId]);
    return (string) ($statement->fetchColumn() ?: 'USER');
}

function require_login(): array
{
    if (empty($_SESSION['user_id'])) {
        flash('Please sign in to continue.', 'warning');
        redirect('/user/login.php');
    }

    $statement = db()->prepare('SELECT user_id, name, email, phone, cash_balance, account_status FROM Users WHERE user_id = ?');
    $statement->execute([(int) $_SESSION['user_id']]);
    $user = $statement->fetch();
    if (!$user || $user['account_status'] !== 'ACTIVE') {
        $_SESSION = [];
        flash('Your account is not active.', 'danger');
        redirect('/user/login.php');
    }
    $user['role'] = current_role((int) $user['user_id']);
    $_SESSION['user_role'] = $user['role'];
    return $user;
}

function require_role(array $roles): array
{
    $user = require_login();
    if (!in_array($user['role'], $roles, true)) {
        http_response_code(403);
        exit('Access denied.');
    }
    return $user;
}

function require_admin(): array
{
    return require_role(['ADMIN', 'SUPER_ADMIN']);
}

function require_super_admin(): array
{
    return require_role(['SUPER_ADMIN']);
}
