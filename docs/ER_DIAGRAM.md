# Entity-Relationship (ER) Diagram
## Stock Market Portfolio Management System

This document outlines the conceptual and logical database design for the Stock Market Portfolio Management System.

### Mermaid ER Diagram

```mermaid
erDiagram
    USERS ||--o{ TRANSACTIONS : places
    USERS ||--o{ PORTFOLIO : owns
    USERS ||--o{ WATCHLIST : monitors
    USERS ||--o{ AUDIT_LOG : generates
    USERS ||--o{ PASSWORD_RESET : requests
    
    STOCKS ||--o{ TRANSACTIONS : "traded in"
    STOCKS ||--o{ PORTFOLIO : "held as"
    STOCKS ||--o{ WATCHLIST : "tracked in"
    STOCKS ||--o{ STOCK_PRICE_HISTORY : "records history"

    USERS {
        int user_id PK
        string name
        string email UK
        string phone
        string password_hash
        decimal cash_balance
        enum account_status
        timestamp created_at
        timestamp updated_at
    }

    STOCKS {
        int stock_id PK
        string symbol UK
        string company_name
        string sector
        decimal current_price
        decimal day_change
        decimal day_change_percent
        decimal high_52w
        decimal low_52w
        bigint volume
        timestamp updated_at
    }

    TRANSACTIONS {
        int transaction_id PK
        int user_id FK
        int stock_id FK
        enum transaction_type
        int quantity
        decimal price
        decimal total_amount
        date transaction_date
        time transaction_time
        enum transaction_status
        timestamp created_at
    }

    PORTFOLIO {
        int portfolio_id PK
        int user_id FK
        int stock_id FK
        int total_quantity
        decimal average_buy_price
        timestamp updated_at
    }

    WATCHLIST {
        int watchlist_id PK
        int user_id FK
        int stock_id FK
        timestamp added_at
    }

    ADMIN {
        int admin_id PK
        string username UK
        string email UK
        string password_hash
        string role
        timestamp created_at
    }

    AUDIT_LOG {
        int log_id PK
        int user_id FK
        string action
        string table_name
        int record_id
        timestamp action_timestamp
        text description
    }

    PASSWORD_RESET {
        int reset_id PK
        int user_id FK
        string reset_token_hash
        datetime expiry_time
        boolean is_used
        timestamp created_at
    }

    STOCK_PRICE_HISTORY {
        int history_id PK
        int stock_id FK
        decimal price
        timestamp recorded_at
    }
```

### Entity Descriptions and Cardinality Relationships

1. **USERS to TRANSACTIONS (1 : N)**
   - **Cardinality**: One User can execute zero, one, or many Transactions ($1 : N$).
   - **Participation**: Optional on Users side (a newly registered user has 0 transactions), Mandatory on Transactions side (every transaction must belong to exactly one user).
   - **Referential Action**: `ON DELETE RESTRICT` to preserve immutable financial audit logs.

2. **STOCKS to TRANSACTIONS (1 : N)**
   - **Cardinality**: One Stock can appear in multiple Transactions ($1 : N$).
   - **Participation**: Mandatory on Transactions side (every transaction must reference a valid stock).
   - **Referential Action**: `ON DELETE RESTRICT` to maintain transaction records.

3. **USERS to STOCKS through PORTFOLIO (M : N)**
   - **Cardinality**: Many Users can own Many Stocks ($M : N$).
   - **Resolution**: Resolved through associative junction entity `PORTFOLIO` with composite uniqueness `(user_id, stock_id)`.
   - **Attributes**: `total_quantity`, `average_buy_price`, `updated_at`.

4. **USERS to STOCKS through WATCHLIST (M : N)**
   - **Cardinality**: Many Users can monitor Many Stocks ($M : N$).
   - **Resolution**: Resolved through associative junction entity `WATCHLIST` with composite uniqueness `(user_id, stock_id)`.

5. **STOCKS to STOCK_PRICE_HISTORY (1 : N)**
   - **Cardinality**: One Stock has many historical price records ($1 : N$).
   - **Referential Action**: `ON DELETE CASCADE` so deleting a stock cleans up historical ticks.

6. **USERS to AUDIT_LOG (1 : N)**
   - **Cardinality**: One User can generate multiple audit entries ($1 : N$).
   - **Referential Action**: `ON DELETE SET NULL` to preserve security audit history even if user profile is purged.
