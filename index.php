<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/bootstrap.php';
require_once __DIR__ . '/includes/layout.php';

if (!empty($_SESSION['user_id'])) {
    $role = current_role((int) $_SESSION['user_id']);
    redirect($role === 'USER' ? '/user/dashboard.php' : '/admin/dashboard.php');
}

$body = '<div class="auth-page" style="place-items:start center;padding-top:80px"><div class="auth-card" style="max-width:700px;text-align:center">'
    . '<h1>StockPulse</h1><p class="subtitle">Stock market portfolio management and paper trading</p>'
    . '<div class="d-flex justify-content-center gap-3">'
    . '<a class="btn btn-primary" href="/user/login.php">Investor Login</a>'
    . '<a class="btn btn-dark" href="/admin/login.php">Administrator Login</a>'
    . '</div></div></div>';
render_layout('StockPulse', $body);
