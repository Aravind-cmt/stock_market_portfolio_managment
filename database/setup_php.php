<?php
declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    http_response_code(403);
    exit('Run this script from the command line.');
}

require_once __DIR__ . '/../config/database.php';

$host = getenv('MYSQL_HOST') ?: '127.0.0.1';
$port = getenv('MYSQL_PORT') ?: '3306';
$database = getenv('MYSQL_DB') ?: 'stock_portfolio_db';

$admin = new PDO(sprintf('mysql:host=%s;port=%s;charset=utf8mb4', $host, $port), getenv('MYSQL_USER') ?: 'root', getenv('MYSQL_PASSWORD') ?: '', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$admin->exec("CREATE DATABASE IF NOT EXISTS `$database` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
$admin->exec("USE `$database`");

$schema = file_get_contents(__DIR__ . '/schema.sql');
if ($schema === false) exit("Unable to read schema.sql\n");
$schema = str_replace('CREATE DATABASE IF NOT EXISTS stock_portfolio_db', 'CREATE DATABASE IF NOT EXISTS `' . str_replace('`', '``', $database) . '`', $schema);
$schema = str_replace('USE stock_portfolio_db;', "USE `$database`;", $schema);
foreach (array_filter(array_map('trim', explode(';', $schema))) as $statement) {
    try { $admin->exec($statement); } catch (PDOException $error) { fwrite(STDERR, "Schema notice: " . $error->getMessage() . "\n"); }
}

$pdo = db();
$pdo->exec("INSERT IGNORE INTO Roles (role_id,role_name) VALUES (1,'SUPER_ADMIN'),(2,'ADMIN'),(3,'USER')");

$passwords = [
    'superadmin@stockpulse.com' => 'Admin@123',
    'admin@stockpulse.com' => 'Admin@123',
];
$statement = $pdo->prepare('SELECT user_id,password_hash FROM Users WHERE email=?');
foreach ($passwords as $email => $password) {
    $statement->execute([$email]);
    $user = $statement->fetch();
    if ($user) {
        $pdo->prepare('UPDATE Users SET password_hash=? WHERE user_id=?')->execute([password_hash($password, PASSWORD_DEFAULT), (int) $user['user_id']]);
    }
}
foreach ([3,4,5,6,7,8,9,10,11,12] as $userId) {
    $passwordHash = password_hash('Password@123', PASSWORD_DEFAULT);
    $pdo->prepare('UPDATE Users SET password_hash=? WHERE user_id=?')->execute([$passwordHash,$userId]);
}

echo "PHP/MySQL setup completed.\n";
