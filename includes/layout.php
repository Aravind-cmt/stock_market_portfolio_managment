<?php
declare(strict_types=1);

function render_layout(string $title, string $body, ?array $user = null, bool $admin = false): void
{
    $role = $user['role'] ?? 'GUEST';
    $messages = consume_flash();
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>' . e($title) . ' - StockPulse</title>';
    echo '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">';
    echo '<link rel="stylesheet" href="/assets/css/style.css">';
    echo '</head><body>';
    echo '<div class="app-shell">';
    if ($user) {
        echo '<aside class="sidebar">';
        echo '<a class="brand" href="' . ($admin ? '/admin/dashboard.php' : '/user/dashboard.php') . '">StockPulse</a>';
        echo '<nav>';
        if ($admin) {
            echo '<a href="/admin/dashboard.php">Dashboard</a>';
            echo '<a href="/admin/users.php">Users</a>';
            echo '<a href="/admin/stocks.php">Stocks</a>';
            echo '<a href="/admin/transactions.php">Transactions</a>';
            if ($role === 'SUPER_ADMIN') {
                echo '<a href="/admin/admins.php">Admin Management</a>';
                echo '<a href="/admin/audit-logs.php">Audit Logs</a>';
            }
        } else {
            echo '<a href="/user/dashboard.php">Dashboard</a>';
            echo '<a href="/user/market.php">Market</a>';
            echo '<a href="/user/portfolio.php">Portfolio</a>';
            echo '<a href="/user/trade.php">Trade</a>';
            echo '<a href="/user/watchlist.php">Watchlist</a>';
            echo '<a href="/user/transactions.php">Transactions</a>';
            echo '<a href="/reports/index.php">Reports</a>';
        }
        echo '<a href="/' . ($admin ? 'admin/logout.php' : 'user/logout.php') . '" class="logout">Logout</a>';
        echo '</nav></aside>';
    }
    echo '<main class="main-content">';
    foreach ($messages as $message) {
        $type = e($message['type']);
        echo '<div class="alert alert-' . $type . '">' . e($message['message']) . '</div>';
    }
    echo '<div class="page-header"><h1>' . e($title) . '</h1>';
    if ($user) {
        echo '<div class="account-meta"><span>' . e($user['name']) . '</span><span class="badge-role">' . e($role) . '</span></div>';
    }
    echo '</div>';
    echo $body;
    echo '</main></div>';
    echo '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>';
    echo '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>';
    echo '<script src="/assets/js/app.js"></script>';
    echo '</body></html>';
}
