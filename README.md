# Money Tracker API - Newbie Guide

A simple API to track money across multiple wallets. Each user can have several wallets (e.g. personal, business), and each wallet can have income (Credit) and expense (Debit) transactions.

---

## Table of Contents

1. [What You Need Before Starting](#1-what-you-need-before-starting)
2. [Complete End-to-End Flow (DB to APIs)](#2-complete-end-to-end-flow-db-to-apis) **<-- Start here!**
3. [Project Structure (What's What)](#3-project-structure-whats-what)
4. [Step-by-Step Setup](#4-step-by-step-setup)
5. [Understanding the Database](#5-understanding-the-database)
6. [Creating Test Data](#6-creating-test-data)
7. [Running the Application](#7-running-the-application)
8. [How to Access Each API Endpoint](#8-how-to-access-each-api-endpoint)
9. [Application Flow (How It Works)](#9-application-flow-how-it-works)

---

## 1. What You Need Before Starting

| Requirement | What It Is |
|-------------|------------|
| **Python 3.10+** | Programming language used by this project |
| **pip** | Tool to install Python packages |
| **Terminal/Command Prompt** | Where you run commands |

**Check if you have them:**

```bash
python --version
pip --version
```

---

## 2. Complete End-to-End Flow (DB to APIs)

This section shows the **exact order** of steps from database setup to calling all APIs. Follow this sequence.

### Flow Overview

```
[1. Install] -> [2. DB Setup] -> [3. Create Data] -> [4. Start Server] -> [5. Call APIs]
     |                |                  |                   |                    |
     pip          migrations         User+Wallet        runserver          POST/GET
```

### Step 1: Install Dependencies

```powershell
cd C:\Users\JobMasai
pip install -r requirements.txt
```

### Step 2: Database Setup (Create Tables)

```powershell
# Create migration files from models
python manage.py makemigrations

# Apply migrations - creates db.sqlite3 and tables (users, user_wallets, transactions)
python manage.py migrate
```

**Result:** `db.sqlite3` file is created. Tables: `users`, `user_wallets`, `transactions`.

### Step 3: Create Test Data (User + Wallet)

**Option A - One-time via shell:**

```powershell
python manage.py shell -c "
from wallets.models import Account, UserWallet
u = Account.objects.create(first_name='John', last_name='Doe', email='john@example.com', active=True)
w = UserWallet.objects.create(name='Main Wallet', user=u, currency='KES', description='Personal')
print('User ID:', u.id, '| Wallet ID:', w.id)
"
```

**Option B - Via Admin (create superuser first):**

```powershell
python manage.py createsuperuser
# Enter: admin / admin@test.com / admin123

python manage.py runserver
# Open http://127.0.0.1:8000/admin/ -> Add Account -> Add User Wallet
```

**Remember:** You need `user_id` and `wallet_id` for the APIs. Example: User ID = 1, Wallet ID = 1.

### Step 4: Start the Server

```powershell
python manage.py runserver
```

Server runs at **http://127.0.0.1:8000/**. Keep this terminal open.

### Step 5: Call the APIs (In Order)

Open a **new** PowerShell window. Replace `1` with your actual user_id/wallet_id if different.

| Step | API | Purpose |
|------|-----|---------|
| 5a | **Create Transaction** | Add money (Credit) or spend (Debit) |
| 5b | **Get User Wallets** | See all wallets + balances + transactions for a user |
| 5c | **Get Wallet Details** | See one wallet's balance + transactions |

---

**5a. Create a Transaction** (POST)

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/transactions/create" -Method POST -ContentType "application/json" -Body '{"user_id":1,"amount":500,"transaction_type":"Credit","currency":"KES","narration":"Salary","reference":"TXN-001","payment_method":"M-Pesa"}'
```

---

**5b. Get All Wallets for User** (GET) - use the `user_id` from Step 3

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/1/wallets" -Method GET
```

---

**5c. Get Single Wallet Details** (GET) - use the `wallet_id` from Step 3

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/wallets/1" -Method GET
```

---

### Flow Summary

| Order | Action | Command/Location |
|-------|--------|------------------|
| 1 | Install | `pip install -r requirements.txt` |
| 2 | DB Setup | `python manage.py migrate` |
| 3 | Create User + Wallet | Django shell or Admin |
| 4 | Start Server | `python manage.py runserver` |
| 5a | Create Transaction | `POST http://127.0.0.1:8000/api/transactions/create` |
| 5b | Get User Wallets | `GET http://127.0.0.1:8000/api/users/1/wallets` |
| 5c | Get Wallet Detail | `GET http://127.0.0.1:8000/api/wallets/1` |

### How DB Tables Connect to APIs

```
DATABASE (db.sqlite3)                    API ENDPOINTS
====================                    =============

users table  ---------------->  GET /api/users/{id}/wallets
  (id, first_name, etc.)         (returns user + their wallets)

user_wallets table ---------->  GET /api/wallets/{id}
  (id, user_id, currency, etc.)   (returns wallet balance + transactions)
       |
       v
transactions table ---------->  POST /api/transactions/create
  (amount, type, wallet_id)       (inserts new row here)
```

- **Create Transaction (POST):** Writes a new row into `transactions`; links to `user_wallets` via `user_id` + `currency`.
- **Get User Wallets (GET):** Reads from `users` and `user_wallets`, computes balance from `transactions`.
- **Get Wallet Detail (GET):** Reads from `user_wallets` and `transactions` for that wallet.

---

## 3. Project Structure (What's What)

```
money_tracker_project/
?
??? manage.py              ? Main command tool (run server, migrations, etc.)
??? requirements.txt       ? List of Python packages needed
??? db.sqlite3             ? Database file (created after migrations)
?
??? money_tracker/         ? Project settings
?   ??? settings.py        ? App config, database, installed apps
?   ??? urls.py            ? Main URL routing (admin + api/)
?
??? wallets/               ? Main app (your business logic)
    ??? models.py          ? Database tables (Account, UserWallet, Transaction)
    ??? views.py           ? Handles API requests (e.g. create transaction)
    ??? serializers.py     ? Validates incoming data
    ??? urls.py            ? API routes (e.g. /api/transactions/create)
    ??? admin.py           ? Registers models for Django admin
```

---

## 4. Step-by-Step Setup

### Step 3.1 - Open Terminal in Project Folder

Navigate to the project root (where `manage.py` is):

```bash
cd C:\Users\JobMasai
```

### Step 3.2 - Create a Virtual Environment (Recommended)

Keeps project dependencies separate from other Python projects:

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

### Step 3.3 - Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Django and Django REST Framework.

---

## 5. Understanding the Database

The app uses **SQLite** (a file-based database). No separate database server is needed.

### Tables and Relationships

```
???????????????????       ???????????????????       ???????????????????
?     Account     ?       ?   UserWallet    ?       ?   Transaction   ?
?   (users table) ?       ? (user_wallets)  ?       ?  (transactions) ?
???????????????????       ???????????????????       ???????????????????
? id              ????    ? id              ????    ? id              ?
? first_name      ?  ?    ? name            ?  ?    ? amount          ?
? last_name       ?  ?????? user_id (FK)    ?  ?????? user_wallet_id  ?
? email           ?       ? currency (KES,  ?       ? transaction_type?
? phone_number    ?       ?         USD)    ?       ?   (Credit/Debit)?
? active          ?       ? description     ?       ? narration       ?
???????????????????       ???????????????????       ???????????????????

  One user          One user can have        Each transaction
  has many          many wallets             belongs to one wallet
  wallets           (one per currency)       (Income or Expense)
```

### Create and Apply Migrations

Migrations tell Django how to create or change database tables:

```bash
# Generate migration files from models
python manage.py makemigrations

# Apply them to the database
python manage.py migrate
```

After this, `db.sqlite3` will be created in the project folder.

---

## 6. Creating Test Data

You need at least one **Account** (user) and one **UserWallet** before the API can create transactions.

### Option A - Django Admin (Easiest)

**1. Create an admin account:**

```bash
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

**2. Start the server:**

```bash
python manage.py runserver
```

**3. Open:** http://127.0.0.1:8000/admin/

**4. Log in** with your superuser account.

**5. Add data:**
- Go to **Accounts** > Add Account (e.g. John Doe, john@example.com)
- Go to **User Wallets** > Add User Wallet (choose the user, name, currency e.g. KES or USD)

### Option B - Django Shell (For Scripts)

```bash
python manage.py shell
```

Then run:

```python
from wallets.models import Account, UserWallet

# Create user
user = Account.objects.create(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    active=True
)

# Create wallet for that user (currency: KES or USD)
wallet = UserWallet.objects.create(
    name="Main Wallet",
    user=user,
    currency="KES",
    description="Personal Kenya wallet"
)

print(f"User ID: {user.id}, Wallet ID: {wallet.id}")
```

Use the returned **User ID** when testing the API.

---

## 7. Running the Application

```bash
python manage.py runserver
```

You should see something like:

```
Starting development server at http://127.0.0.1:8000/
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/admin/ | Django admin (manage users, wallets, transactions) |
| http://127.0.0.1:8000/api/transactions/create | Create a transaction (POST) |
| http://127.0.0.1:8000/api/users/{user_id}/wallets | Get all wallets for a user (GET) |
| http://127.0.0.1:8000/api/wallets/{wallet_id} | Get wallet details and transactions (GET) |

---

## 8. How to Access Each API Endpoint

### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transactions/create` | Create a transaction |
| GET | `/api/users/<user_id>/wallets` | Get all wallets for a user (with balance & transactions) |
| GET | `/api/wallets/<wallet_id>` | Get wallet details (balance & transactions list) |

---

### 1. Create a Transaction (POST)

**Endpoint:** `POST http://127.0.0.1:8000/api/transactions/create`

**Request body (JSON):**

```json
{
    "user_id": 1,
    "amount": 100,
    "transaction_type": "Credit",
    "currency": "KES",
    "narration": "Salary deposit",
    "reference": "TXN-2026-001",
    "payment_method": "M-Pesa"
}
```

**Valid values:**
- `transaction_type`: `"Credit"` (income) or `"Debit"` (expense)
- `currency`: Must match an existing wallet (e.g. `"KES"`, `"USD"`)
- `amount`: Positive number (max 10000 for KES/USD)
- `reference`: **Required** - must be unique across all transactions
- `payment_method`: Optional (e.g. M-Pesa, Bank Transfer, Card)

**Test with PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/transactions/create" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_id":1,"amount":100,"transaction_type":"Credit","currency":"KES","narration":"test","reference":"TXN-001","payment_method":"M-Pesa"}'
```

**Expected Success Response (201 Created):**

```json
{
    "id": 1,
    "amount": "100.00",
    "currency": "KES",
    "transaction_type": "Credit",
    "narration": "test",
    "reference": "TXN-001",
    "payment_method": "M-Pesa",
    "created_date": "2026-02-23T19:55:05.100640+00:00"
}
```

---

### 2. Get Wallets by User ID (GET)

**Endpoint:** `GET http://127.0.0.1:8000/api/users/<user_id>/wallets`

Returns all wallets for a user, each with:
- Balance (Credits - Debits)
- All transactions for that wallet
- Total balance across all wallets

**Test with PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/1/wallets" -Method GET
```

**Example Response:**

```json
{
    "user_id": 1,
    "user_name": "John Doe",
    "wallets": [
        {
            "id": 1,
            "name": "Main",
            "currency": "KES",
            "description": "Kenya wallet",
            "balance": 5150.0,
            "transactions": [
                {
                    "id": 7,
                    "amount": "1000.00",
                    "currency": "KES",
                    "transaction_type": "Credit",
                    "narration": "deposit",
                    "reference": "REF-001",
                    "payment_method": "M-Pesa",
                    "created_date": "2026-02-23T20:22:09+00:00"
                }
            ]
        }
    ],
    "total_balance": 5150.0
}
```

---

### 3. Get Individual Wallet Details (GET)

**Endpoint:** `GET http://127.0.0.1:8000/api/wallets/<wallet_id>`

Returns wallet balance and all transactions for that wallet.

**Test with PowerShell:**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/wallets/1" -Method GET
```

**Example Response:**

```json
{
    "wallet_balance": 5150.0,
    "transactions_list": [
        {
            "id": 7,
            "amount": "1000.00",
            "currency": "KES",
            "transaction_type": "Credit",
            "narration": "deposit",
            "reference": "REF-001",
            "payment_method": "M-Pesa",
            "created_date": "2026-02-23T20:22:09+00:00"
        }
    ]
}
```

---

### Error Responses (400 Bad Request)

| Error | Meaning |
|-------|---------|
| `"Invalid user details provided"` | User doesn't exist or is not active |
| `"Unable to deposit funds in the provided wallet"` | User has no wallet for that currency |
| `"Invalid amount provided"` | Amount is zero or negative |
| `"Unable to deposit using the provided amount."` | Amount exceeds max (10000 for KES/USD) |
| `"Transaction type must be Credit or Debit"` | Invalid `transaction_type` |
| `"A transaction with this reference already exists."` | Duplicate `reference` (must be unique) |

### Access Methods Summary

You can call these APIs using:

| Method | Use Case |
|--------|----------|
| **PowerShell** | `Invoke-RestMethod` (examples below) |
| **cURL** | Command line (Windows/Linux/Mac) |
| **Browser** | GET endpoints only - paste URL in address bar |
| **Postman/Insomnia** | GUI API clients |
| **JavaScript fetch** | From a frontend app |

### Full URLs (replace IDs as needed)

| API | Full URL | Method |
|-----|----------|--------|
| Create Transaction | `http://127.0.0.1:8000/api/transactions/create` | POST |
| Get User Wallets | `http://127.0.0.1:8000/api/users/1/wallets` | GET |
| Get Wallet Detail | `http://127.0.0.1:8000/api/wallets/1` | GET |

**Browser:** For GET requests only, open `http://127.0.0.1:8000/api/users/1/wallets` or `http://127.0.0.1:8000/api/wallets/1` in Chrome/Edge. You will see the JSON response.

**cURL (Create Transaction):**

```bash
curl -X POST http://127.0.0.1:8000/api/transactions/create -H "Content-Type: application/json" -d "{\"user_id\":1,\"amount\":100,\"transaction_type\":\"Credit\",\"currency\":\"KES\",\"narration\":\"test\",\"reference\":\"TXN-002\",\"payment_method\":\"M-Pesa\"}"
```

**cURL (Get User Wallets):**

```bash
curl http://127.0.0.1:8000/api/users/1/wallets
```

**cURL (Get Wallet Detail):**

```bash
curl http://127.0.0.1:8000/api/wallets/1
```

---

## 9. Application Flow (How It Works)

### Request flow for creating a transaction

```
1. Client sends POST request
   - URL: /api/transactions/create
   - Body: { user_id, amount, transaction_type, currency, narration, reference, payment_method }

2. Django receives request
   - money_tracker/urls.py routes to wallets app
   - wallets/urls.py routes to the appropriate view

3. TransactionCreateView (for POST /api/transactions/create)
   - Passes request data to TransactionCreateSerializer
   - Validates user exists and is active
   - Validates user has a wallet for that currency
   - Validates amount > 0 and within limits
   - Validates transaction_type is Credit or Debit
   - Validates reference is unique

4. Get Wallets / Wallet Detail views (for GET requests)
   - Query wallets and transactions by user_id or wallet_id
   - Calculate balance (Credits - Debits) per wallet
   - Return JSON response
```

### Balance calculation

- **Credit** (income) - adds to wallet balance  
- **Debit** (expense) - subtracts from wallet balance  

Example: 3 transactions (Credit 100, Credit 50, Debit 30) -> Balance = 120

---

## Quick Reference - Common Commands

| Command | What It Does |
|---------|--------------|
| `pip install -r requirements.txt` | Install dependencies |
| `python manage.py makemigrations` | Create migration files |
| `python manage.py migrate` | Apply migrations to database |
| `python manage.py createsuperuser` | Create admin account |
| `python manage.py runserver` | Start development server |
| `python manage.py shell` | Open Django Python shell |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'django'` | Run `pip install -r requirements.txt` |
| `Invalid user details provided` | Create an Account and UserWallet first (via admin or shell) |
| `Unable to deposit funds in the provided wallet` | Create a wallet with that currency for that user |
| Admin login fails | Run `python manage.py createsuperuser` to create an admin user |

---

**Happy coding!**
