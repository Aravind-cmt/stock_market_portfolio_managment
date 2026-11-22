<?php
declare(strict_types=1);

function render_layout(string $title, string $body, ?array $user = null, bool $admin = false): void
{
    $role = $user['role'] ?? 'GUEST';
    $messages = consume_flash();
    $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '';
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>' . e($title) . ' - StockPulse</title>';
    echo '<link rel="preconnect" href="https://fonts.googleapis.com">';
    echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>';
    echo '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap" rel="stylesheet">';
    echo '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">';
    echo '<link rel="stylesheet" href="/assets/css/style.css">';
    echo '</head><body>';
    echo '<div class="app-shell' . (!$user ? ' auth-shell' : '') . '">';
    if ($user) {
        echo '<aside class="sidebar">';
        echo '<button class="sidebar-close" type="button" aria-label="Close navigation">×</button>';
        echo '<a class="brand" href="' . ($admin ? '/admin/dashboard.php' : '/user/dashboard.php') . '"><span>Stock</span>Pulse</a>';
        echo '<div class="sidebar-section">' . ($admin ? 'Administration' : 'Portfolio') . '</div>';
        echo '<nav>';
        if ($admin) {
            echo '<a class="' . ($path === '/admin/dashboard.php' ? 'active' : '') . '" href="/admin/dashboard.php">Dashboard</a>';
            echo '<a class="' . ($path === '/admin/users.php' ? 'active' : '') . '" href="/admin/users.php">Users</a>';
            echo '<a class="' . ($path === '/admin/stocks.php' ? 'active' : '') . '" href="/admin/stocks.php">Stocks</a>';
            echo '<a class="' . ($path === '/admin/transactions.php' ? 'active' : '') . '" href="/admin/transactions.php">Transactions</a>';
            if ($role === 'SUPER_ADMIN') {
                echo '<a class="' . ($path === '/admin/admins.php' || $path === '/admin/add-admin.php' ? 'active' : '') . '" href="/admin/admins.php">Admin Management</a>';
                echo '<a class="' . ($path === '/admin/audit-logs.php' ? 'active' : '') . '" href="/admin/audit-logs.php">Audit Logs</a>';
            }
        } else {
            echo '<a class="' . ($path === '/user/dashboard.php' ? 'active' : '') . '" href="/user/dashboard.php">Dashboard</a>';
            echo '<a class="' . ($path === '/user/market.php' ? 'active' : '') . '" href="/user/market.php">Market</a>';
            echo '<a class="' . ($path === '/user/portfolio.php' ? 'active' : '') . '" href="/user/portfolio.php">Portfolio</a>';
            echo '<a class="' . ($path === '/user/trade.php' ? 'active' : '') . '" href="/user/trade.php">Trade</a>';
            echo '<a class="' . ($path === '/user/watchlist.php' ? 'active' : '') . '" href="/user/watchlist.php">Watchlist</a>';
            echo '<a class="' . ($path === '/user/transactions.php' ? 'active' : '') . '" href="/user/transactions.php">Transactions</a>';
            echo '<a class="' . (str_starts_with($path, '/reports/') ? 'active' : '') . '" href="/reports/index.php">Reports</a>';
            echo '<a class="' . ($path === '/user/profile.php' ? 'active' : '') . '" href="/user/profile.php">Profile</a>';
        }
        echo '<a href="/' . ($admin ? 'admin/logout.php' : 'user/logout.php') . '" class="logout">Logout</a>';
        echo '</nav></aside>';
    }
    echo '<main class="main-content">';
    if ($user) {
        echo '<button class="sidebar-toggle" type="button" aria-label="Open navigation">Menu</button>';
    }
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
