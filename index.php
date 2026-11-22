<?php
declare(strict_types=1);
require_once __DIR__ . '/includes/bootstrap.php';
require_once __DIR__ . '/includes/layout.php';

if (!empty($_SESSION['user_id'])) {
    $role = current_role((int) $_SESSION['user_id']);
    redirect($role === 'USER' ? '/user/dashboard.php' : '/admin/dashboard.php');
}

$body = '<section class="auth-page"><div class="landing-panel">'
    . '<div><span class="landing-label">StockPulse Portfolio</span><h1>Portfolio management for informed investing</h1>'
    . '<p>Monitor holdings, execute paper trades, and review portfolio performance in one focused workspace.</p>'
    . '<div class="landing-actions"><a class="btn btn-primary" href="/user/login.php">Investor Login</a>'
    . '<a class="btn btn-outline-primary" href="/admin/login.php">Administrator Login</a></div></div>'
    . '<div class="landing-summary"><div><span>Portfolio</span><strong>Holdings</strong></div><div><span>Trading</span><strong>Buy and Sell</strong></div><div><span>Reporting</span><strong>Transactions</strong></div></div>'
    . '</div></section>';
render_layout('StockPulse', $body);
