# Database Normalization Process & Proof
## Stock Market Portfolio Management System

Database normalization is a systematic approach of decomposing tables to eliminate data redundancy and undesirable anomalies (Insertion, Update, and Deletion anomalies) while preserving data integrity and functional dependencies.

---

### 1. Initial Unnormalized Form (UNF)

In an unnormalized stock system, a single table might record everything together:

$$\text{UNF\_Investment}(\underline{\text{user\_id}}, \text{user\_name}, \text{user\_email}, \text{phone}, \{\text{stock\_symbol}, \text{company\_name}, \text{sector}, \text{buy\_price}, \text{quantity}, \text{trade\_date}\})$$

#### Anomalies in UNF:
- **Repeating Groups**: A user has multiple stock holdings in a multi-valued set.
- **Redundancy**: Repeating user profile and company info with every transaction.
- **Update Anomaly**: If a company changes its sector, every transaction row must be updated.
- **Deletion Anomaly**: If a user sells all shares of a stock, historical company records might be inadvertently wiped out.

---

### 2. First Normal Form (1NF)

**Rule for 1NF**:
1. All attributes must be atomic (indivisible single values).
2. No repeating groups or arrays.
3. A unique primary key must identify each tuple.

**Transformation**:
- Flatten the repeating group into individual rows.
- Define a composite primary key: $(\text{user\_id}, \text{stock\_symbol}, \text{trade\_date})$.

$$\text{Table 1NF}(\underline{\text{user\_id}}, \underline{\text{stock\_symbol}}, \underline{\text{trade\_date}}, \text{user\_name}, \text{user\_email}, \text{phone}, \text{company\_name}, \text{sector}, \text{quantity}, \text{buy\_price})$$

#### Remaining Problems in 1NF:
Partial Functional Dependencies exist because attributes depend on only a *part* of the composite primary key.

---

### 3. Second Normal Form (2NF)

**Rule for 2NF**:
1. The relation must be in 1NF.
2. Every non-prime attribute must be **fully functionally dependent** on the whole primary key (No Partial Dependencies).

**Analysis of Functional Dependencies (FDs)**:
- $FD_1: \text{user\_id} \rightarrow \text{user\_name}, \text{user\_email}, \text{phone}, \text{cash\_balance}$ (Depends only on $\text{user\_id}$)
- $FD_2: \text{stock\_id} \rightarrow \text{symbol}, \text{company\_name}, \text{sector}, \text{current\_price}$ (Depends only on $\text{stock\_id}$)
- $FD_3: (\text{user\_id}, \text{stock\_id}) \rightarrow \text{total\_quantity}, \text{average\_buy\_price}$ (Fully depends on composite key)
- $FD_4: \text{transaction\_id} \rightarrow \text{user\_id}, \text{stock\_id}, \text{transaction\_type}, \text{quantity}, \text{price}, \text{transaction\_date}$

**Decomposition into 2NF**:
1. **Users** Table: Non-prime attributes depend only on `user_id`.
2. **Stocks** Table: Non-prime attributes depend only on `stock_id`.
3. **Portfolio** Table: Non-prime attributes depend fully on `(user_id, stock_id)`.
4. **Transactions** Table: Non-prime attributes depend fully on `transaction_id`.

---

### 4. Third Normal Form (3NF)

**Rule for 3NF**:
1. The relation must be in 2NF.
2. No non-prime attribute should be **transitively dependent** on the primary key ($X \rightarrow Y$ and $Y \rightarrow Z \implies X \rightarrow Z$).

**Verification of All System Tables**:

1. **Users**:
   - Primary Key: `user_id`
   - Dependencies: $\text{user\_id} \rightarrow \text{name}, \text{email}, \text{phone}, \text{password\_hash}, \text{cash\_balance}, \text{account\_status}$
   - No transitive dependencies between non-key attributes. $\implies \mathbf{3NF\text{ Satisfied}}$.

2. **Stocks**:
   - Primary Key: `stock_id`
   - Dependencies: $\text{stock\_id} \rightarrow \text{symbol}, \text{company\_name}, \text{sector}, \text{current\_price}, \text{volume}$
   - Each company belongs to a sector, but sector does not determine company name or price. $\implies \mathbf{3NF\text{ Satisfied}}$.

3. **Transactions**:
   - Primary Key: `transaction_id`
   - Foreign Keys: `user_id`, `stock_id`
   - Non-key attributes: `transaction_type`, `quantity`, `price`, `total_amount`, `transaction_date`, `transaction_time`
   - Derived attributes like total amount are stored explicitly for immutable historical pricing compliance without transitive functional dependency on other entities. $\implies \mathbf{3NF\text{ Satisfied}}$.

4. **Portfolio**:
   - Primary Key: `portfolio_id`
   - Candidate Key: `(user_id, stock_id)`
   - Non-key attributes: `total_quantity`, `average_buy_price`, `updated_at`
   - All non-key attributes directly depend on the candidate key. $\implies \mathbf{3NF\text{ Satisfied}}$.

5. **Watchlist**:
   - Primary Key: `watchlist_id`
   - Candidate Key: `(user_id, stock_id)`
   - Non-key attribute: `added_at` $\implies \mathbf{3NF\text{ Satisfied}}$.

---

### 5. Summary of Normalization Benefits

| Normal Form | Problem Eliminated | Achieved In Our Schema |
|-------------|--------------------|------------------------|
| **1NF** | Multi-valued repeating groups, irregular structures | Atomic attributes for every column |
| **2NF** | Partial dependencies on composite keys | Separate entities for Users, Stocks, Transactions, Portfolio |
| **3NF** | Transitive dependencies between non-key fields | No non-key attributes determining other non-key attributes |
| **BCNF** | Every determinant is a candidate key | Primary keys & Unique constraints are sole determinants |
