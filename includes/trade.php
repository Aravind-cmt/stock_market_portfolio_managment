<?php
declare(strict_types=1);

function execute_buy(int $userId, int $stockId, int $quantity): array
{
    if ($quantity <= 0) return ['success'=>false,'message'=>'Quantity must be greater than zero.'];
    $pdo=db();$pdo->beginTransaction();
    try {
        $u=$pdo->prepare("SELECT cash_balance,account_status FROM Users WHERE user_id=? FOR UPDATE");$u->execute([$userId]);$user=$u->fetch();
        $s=$pdo->prepare("SELECT current_price FROM Stocks WHERE stock_id=? FOR UPDATE");$s->execute([$stockId]);$stock=$s->fetch();
        if(!$user||$user['account_status']!=='ACTIVE')throw new RuntimeException('Investor account is not active.');
        if(!$stock)throw new RuntimeException('Stock not found.');
        $price=(float)$stock['current_price'];$cash=(float)$user['cash_balance'];$total=round($price*$quantity,2);
        if($cash<$total)throw new RuntimeException('Insufficient cash balance.');
        $pdo->prepare("UPDATE Users SET cash_balance=cash_balance-? WHERE user_id=?")->execute([$total,$userId]);
        $tx=$pdo->prepare("INSERT INTO Transactions (user_id,stock_id,transaction_type,quantity,price,total_amount,transaction_date,transaction_time,transaction_status) VALUES (?,?, 'BUY',?,?,?,CURDATE(),CURTIME(),'COMPLETED')");
        $tx->execute([$userId,$stockId,$quantity,$price,$total]);$txId=(int)$pdo->lastInsertId();
        $p=$pdo->prepare("SELECT portfolio_id,total_quantity,average_buy_price FROM Portfolio WHERE user_id=? AND stock_id=? FOR UPDATE");$p->execute([$userId,$stockId]);$holding=$p->fetch();
        if($holding){
            $oldQty=(int)$holding['total_quantity'];$oldAvg=(float)$holding['average_buy_price'];$newQty=$oldQty+$quantity;$newAvg=round((($oldQty*$oldAvg)+($quantity*$price))/$newQty,2);
            $pdo->prepare("UPDATE Portfolio SET total_quantity=?,average_buy_price=?,updated_at=CURRENT_TIMESTAMP WHERE portfolio_id=?")->execute([$newQty,$newAvg,(int)$holding['portfolio_id']]);
        }else{$pdo->prepare("INSERT INTO Portfolio (user_id,stock_id,total_quantity,average_buy_price) VALUES (?,?,?,?)")->execute([$userId,$stockId,$quantity,$price]);}
        $pdo->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,previous_value,new_value,description) VALUES (?,?,?,?,?,?,?,?)")
            ->execute([$userId,$userId,'BUY_ORDER','Transactions',$txId,'Cash: ₹'.$cash,'Cash: ₹'.($cash-$total),"Bought $quantity shares"]);
        $pdo->commit();return ['success'=>true,'message'=>'Purchase completed successfully.'];
    }catch(Throwable $error){if($pdo->inTransaction())$pdo->rollBack();return ['success'=>false,'message'=>$error->getMessage()];}
}

function execute_sell(int $userId,int $stockId,int $quantity):array
{
    if($quantity<=0)return['success'=>false,'message'=>'Quantity must be greater than zero.'];
    $pdo=db();$pdo->beginTransaction();
    try{
        $u=$pdo->prepare("SELECT cash_balance,account_status FROM Users WHERE user_id=? FOR UPDATE");$u->execute([$userId]);$user=$u->fetch();
        $p=$pdo->prepare("SELECT portfolio_id,total_quantity,average_buy_price FROM Portfolio WHERE user_id=? AND stock_id=? FOR UPDATE");$p->execute([$userId,$stockId]);$holding=$p->fetch();
        $s=$pdo->prepare("SELECT current_price FROM Stocks WHERE stock_id=? FOR UPDATE");$s->execute([$stockId]);$stock=$s->fetch();
        if(!$user||$user['account_status']!=='ACTIVE')throw new RuntimeException('Investor account is not active.');
        if(!$stock)throw new RuntimeException('Stock not found.');
        if(!$holding||(int)$holding['total_quantity']<$quantity)throw new RuntimeException('Insufficient shares owned.');
        $price=(float)$stock['current_price'];$total=round($price*$quantity,2);$avg=(float)$holding['average_buy_price'];$pnl=round(($price-$avg)*$quantity,2);$remaining=(int)$holding['total_quantity']-$quantity;
        $pdo->prepare("UPDATE Users SET cash_balance=cash_balance+? WHERE user_id=?")->execute([$total,$userId]);
        $tx=$pdo->prepare("INSERT INTO Transactions (user_id,stock_id,transaction_type,quantity,price,total_amount,transaction_date,transaction_time,transaction_status) VALUES (?,?, 'SELL',?,?,?,CURDATE(),CURTIME(),'COMPLETED')");
        $tx->execute([$userId,$stockId,$quantity,$price,$total]);$txId=(int)$pdo->lastInsertId();
        if($remaining===0)$pdo->prepare("DELETE FROM Portfolio WHERE portfolio_id=?")->execute([(int)$holding['portfolio_id']]);
        else$pdo->prepare("UPDATE Portfolio SET total_quantity=?,updated_at=CURRENT_TIMESTAMP WHERE portfolio_id=?")->execute([$remaining,(int)$holding['portfolio_id']]);
        $pdo->prepare("INSERT INTO Audit_Log (acting_user_id,affected_user_id,action,table_name,record_id,previous_value,new_value,description) VALUES (?,?,?,?,?,?,?,?)")
            ->execute([$userId,$userId,'SELL_ORDER','Transactions',$txId,'Shares: '.((int)$holding['total_quantity']),'Shares: '.$remaining,'Sold '.$quantity.' shares. Realized P&L: ₹'.$pnl]);
        $pdo->commit();return['success'=>true,'message'=>'Sale completed successfully. Realized P&L: ₹'.number_format($pnl,2)];
    }catch(Throwable $error){if($pdo->inTransaction())$pdo->rollBack();return['success'=>false,'message'=>$error->getMessage()];}
}
