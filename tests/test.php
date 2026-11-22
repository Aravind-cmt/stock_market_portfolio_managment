<?php
declare(strict_types=1);

require_once __DIR__ . '/../includes/bootstrap.php';

$pdo = db();
$tests = [];

function test_case(string $name, bool $passed, string $details = ''): void
{
    global $tests;
    $tests[] = [$name, $passed, $details];
    echo ($passed ? 'PASS' : 'FAIL') . ': ' . $name;
    if ($details !== '') echo ' - ' . $details;
    echo PHP_EOL;
}

$requiredTables = ['Users','Roles','User_Roles','Stocks','Transactions','Portfolio','Watchlist','Audit_Log','Password_Reset','Stock_Price_History'];
foreach ($requiredTables as $table) {
    $statement = $pdo->prepare("SELECT COUNT(*) FROM `$table`");
    try { $statement->execute(); test_case("Database table $table", true); }
    catch (Throwable $error) { test_case("Database table $table", false, $error->getMessage()); }
}

$roleCount = $pdo->query("SELECT COUNT(*) FROM Roles WHERE role_name IN ('USER','ADMIN','SUPER_ADMIN')")->fetchColumn();
test_case('Three role names exist', (int)$roleCount === 3);

$passwordHash = password_hash('TestPassword123', PASSWORD_DEFAULT);
test_case('PHP password hashing', password_verify('TestPassword123', $passwordHash));

$hashOnly = $pdo->query("SELECT COUNT(*) FROM Users WHERE password_hash LIKE 'scrypt:%'")->fetchColumn();
test_case('No legacy Scrypt password hashes remain', (int)$hashOnly === 0);
