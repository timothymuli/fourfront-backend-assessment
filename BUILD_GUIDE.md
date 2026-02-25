# Money Tracker API - Step-by-Step Build Guide

**For Complete Beginners**

This guide walks you through building the **entire Money Tracker application from scratch**. Every step includes an explanation of *why* we're doing it, so you understand the full picture—not just copy-pasting code.

---

## What Are We Building? (The Big Picture)

Imagine an app where:
- **Users** can have multiple **wallets** (e.g. one for KES, one for USD)
- Each wallet has **transactions** (money in = Credit, money out = Debit)
- We expose **APIs** so a frontend or mobile app can create transactions and view balances

**You will build:** A backend API (no fancy UI) that stores data in a database and responds to HTTP requests with JSON.

---

## How a Request Flows (Mental Model)

When someone calls `POST /api/transactions/create` with JSON data:

1. **Django** receives the request
2. **URLs** decide which **View** (controller) handles it
3. The **View** uses a **Serializer** to validate the data
4. If valid, the **View** saves to the **database** (via Models)
5. The **View** returns a JSON response

```
Request → URLs → View → Serializer (validates) → Model (saves to DB) → Response
```

Keep this flow in mind as we build each piece.

---

## Prerequisites

- Python 3.10+ installed
- A code editor (VS Code, Cursor, etc.)
- Terminal/Command Prompt

---

# Part 1: Environment Setup

## Step 1.1 - Create Project Folder

```bash
mkdir money_tracker_project
cd money_tracker_project
```

**Why:** We need a dedicated folder so all our files stay together. Think of it as creating a workspace before you start painting.

---

## Step 1.2 - Create Virtual Environment

```bash
python -m venv venv
```

**What is a virtual environment?**  
It’s an isolated space for this project’s Python packages. Without it, every project on your computer would share the same Django version, which can cause conflicts. With `venv`, this project has its own copy of Django and DRF.

**Activate it:**

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (CMD):** `venv\Scripts\activate.bat`
- **Mac/Linux:** `source venv/bin/activate`

You should see `(venv)` in your terminal. That means the virtual environment is active. Anything you install with `pip` will stay inside this project.

---

## Step 1.3 - Install Dependencies

Create a file named `requirements.txt` with:

```
Django>=6.0
djangorestframework>=3.16
```

**Why `requirements.txt`?**  
It lists the packages the project needs. Anyone else (or you on another machine) can run `pip install -r requirements.txt` and get the exact same setup. No guessing versions.

- **Django:** Web framework (handles URLs, database, admin, etc.)
- **djangorestframework:** Adds tools for building REST APIs (serializers, views, JSON responses)

Then run:

```bash
pip install -r requirements.txt
```

---

## Step 1.4 - Create Django Project

```bash
python -m django startproject money_tracker .
```

**Breaking this down:**
- `python -m django` — run Django’s command-line tools
- `startproject money_tracker` — create a project named `money_tracker`
- The `.` at the end — create it in the current folder (not in a subfolder)

**What you get:**
- `manage.py` — main entry point for running commands (migrate, runserver, etc.)
- `money_tracker/` — project configuration (settings, main URLs)

**Verify:** Run `python manage.py runserver` and open http://127.0.0.1:8000/. You should see the Django welcome page. Press `Ctrl+C` to stop the server.

---

# Part 2: Create the Wallets App

In Django, a **project** contains one or more **apps**. The project is the container; apps hold the actual features.

## Step 2.1 - Create the App

```bash
python -m django startapp wallets
```

**Why "wallets"?**  
This app will manage users, wallets, and transactions. Naming it `wallets` keeps it focused.

**What you get:** A `wallets/` folder with `models.py`, `views.py`, `admin.py`, etc. Django generates these files; we’ll fill them in.

---

## Step 2.2 - Register the App

Django must know the app exists. Open `money_tracker/settings.py`, find `INSTALLED_APPS`, and add:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',   # Enables API features (serializers, API views)
    'wallets',          # Our app - Django will load its models, views, etc.
]
```

**Why `rest_framework`?**  
Django alone can serve HTML pages. Django REST Framework adds:
- Serializers (validation, JSON conversion)
- APIView (easy JSON responses)
- Better handling of POST/GET with JSON

**Why `wallets`?**  
Until it’s in `INSTALLED_APPS`, Django ignores it. No models, no URLs, nothing.

---

## Step 2.3 - Add App Config (Max Amounts)

At the bottom of `money_tracker/settings.py`, add:

```python
# Money Tracker - Max deposit amounts per currency
# We use this in our serializer to reject amounts that exceed the limit
MAXIMUM_KES_AMOUNT = 10000
MAXIMUM_USD_AMOUNT = 10000
MAXIMUM_AMOUNTS = {
    'KES': MAXIMUM_KES_AMOUNT,
    'USD': MAXIMUM_USD_AMOUNT,
}
```

**Why store this in settings?**  
So we can change limits without editing serializer code. One place to configure business rules.

---

# Part 3: Build the Models

**What is a Model?**  
A Python class that describes a database table. Each attribute is a column. Django turns this into SQL and creates the table.

**Relationship recap:**
- One **Account** (user) has many **UserWallets**
- One **UserWallet** has many **Transactions**

Open `wallets/models.py` and **replace all content** with:

```python
"""
Models = Database tables. Each class becomes a table, each field becomes a column.
Django handles the SQL; we define structure in Python.
"""

from django.db import models


class Account(models.Model):
    """
    Represents a user (no login/auth - just profile data).
    Table name in DB: users
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=15, blank=True)  # blank=True = optional
    created_date = models.DateTimeField(auto_now_add=True)     # Set automatically when created
    active = models.BooleanField(default=True)                 # Soft delete: inactive users still exist

    class Meta:
        db_table = 'users'           # Use 'users' as table name instead of wallets_account
        ordering = ['-created_date']  # Newest first when we query

    def __str__(self):
        return f"{self.first_name} {self.last_name}"  # Pretty display in admin/shell


class UserWallet(models.Model):
    """
    A wallet belonging to a user. One user can have many wallets (e.g. KES, USD).
    ForeignKey = "this wallet belongs to one Account"
    related_name='wallets' = from an Account, we can do account.wallets.all()
    """
    name = models.CharField(max_length=20)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='wallets')
    # on_delete=CASCADE: if Account is deleted, delete all its wallets too
    description = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=3)  # KES, USD, etc.
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_wallets'
        ordering = ['-created_date']
        # One user can have only ONE wallet per currency
        unique_together = [['user', 'currency']]

    def __str__(self):
        return f"{self.name} ({self.currency})"

    @property
    def balance(self):
        """
        Compute balance: Credits add, Debits subtract.
        @property = we call it as wallet.balance (no parentheses).
        We don't store balance - we calculate it from transactions.
        """
        total = 0
        for txn in self.transactions.all():  # transactions comes from related_name on Transaction
            if txn.transaction_type == 'Credit':
                total += txn.amount
            else:
                total -= txn.amount
        return total


class Transaction(models.Model):
    """
    A single income (Credit) or expense (Debit) in a wallet.
    ForeignKey to UserWallet = each transaction belongs to one wallet.
    """
    TRANSACTION_TYPES = [
        ('Credit', 'Credit'),  # Money in (income)
        ('Debit', 'Debit'),    # Money out (expense)
    ]

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10)
    user_wallet = models.ForeignKey(
        UserWallet, on_delete=models.CASCADE, related_name='transactions'
    )
    # related_name='transactions' = from a UserWallet, we do wallet.transactions.all()
    created_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    narration = models.CharField(max_length=255, blank=True)  # e.g. "Salary deposit"
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    # unique=True = no two transactions can have the same reference
    # null=True, blank=True = old rows (before we added this) can have NULL
    payment_method = models.CharField(max_length=50, blank=True)  # M-Pesa, Card, etc.

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency}"
```

**Key concepts:**
- **ForeignKey:** Links one table to another (e.g. Transaction → UserWallet)
- **related_name:** Lets you go “backwards” (e.g. `wallet.transactions.all()`)
- **@property:** A computed value, not stored in the DB
- **unique_together:** Enforces “one wallet per currency per user”

---

# Part 4: Create Database Tables (Migrations)

Models are Python. The database needs actual tables. **Migrations** are the bridge.

## Step 4.1 - Generate Migrations

```bash
python manage.py makemigrations wallets
```

**What this does:**  
Reads your models and creates migration files that describe the SQL (e.g. “create table users”, “add column reference”). These files live in `wallets/migrations/`.

## Step 4.2 - Apply Migrations

```bash
python manage.py migrate
```

**What this does:**  
Runs the migration SQL against your database. This creates `db.sqlite3` and the `users`, `user_wallets`, and `transactions` tables.

**Verify:** A file `db.sqlite3` should appear. That’s your database.

---

# Part 5: Create the Serializers (Validations)

**What is a Serializer?**  
It:
1. Validates incoming data (e.g. “is user_id valid?”, “is amount positive?”)
2. Converts Python objects to JSON (and vice versa)

When someone sends `POST /api/transactions/create` with JSON, the serializer checks everything before we touch the database.

Create a **new file** `wallets/serializers.py`:

```python
"""
Serializers: Validate incoming request data and convert to/from JSON.
Think of them as the gatekeeper - bad data never reaches the database.
"""

from rest_framework import serializers
from django.conf import settings

from .models import Transaction, Account, UserWallet


class TransactionCreateSerializer(serializers.Serializer):
    """
    Defines what we EXPECT in the request body for creating a transaction.
    Each field = one key in the JSON. required=True means "must be present".
    """
    user_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=True, min_value=0
    )
    transaction_type = serializers.ChoiceField(
        choices=['Credit', 'Debit'],
        required=True
    )
    currency = serializers.CharField(max_length=10, required=True)
    narration = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reference = serializers.CharField(max_length=100, required=True)
    payment_method = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_user_id(self, value):
        """
        Custom validation: user_id must point to a real, active user.
        Naming: validate_<fieldname> - Django REST Framework calls this automatically.
        """
        try:
            Account.objects.get(id=value, active=True)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid user details provided")
        return value

    def validate_amount(self, value):
        """Amount must be positive. Zero or negative = reject."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Invalid amount provided")
        return value

    def validate_transaction_type(self, value):
        """Only Credit or Debit allowed."""
        if value not in ['Credit', 'Debit']:
            raise serializers.ValidationError(
                "Transaction type must be Credit or Debit"
            )
        return value

    def validate_reference(self, value):
        """Reference must be unique - no duplicate transaction IDs from client."""
        if Transaction.objects.filter(reference=value).exists():
            raise serializers.ValidationError(
                "A transaction with this reference already exists."
            )
        return value

    def validate(self, attrs):
        """
        Cross-field validation - runs after all individual field validations.
        Here we check: does this user have a wallet with this currency?
        We also check amount vs MAXIMUM_AMOUNTS from settings.
        """
        user_id = attrs['user_id']
        currency = attrs.get('currency', '').upper()

        try:
            wallet = UserWallet.objects.get(user_id=user_id, currency=currency)
        except UserWallet.DoesNotExist:
            raise serializers.ValidationError(
                "Unable to deposit funds in the provided wallet"
            )

        # Check max amount from settings (e.g. 10000 for KES)
        max_amounts = getattr(settings, 'MAXIMUM_AMOUNTS', {})
        max_allowed = max_amounts.get(currency)
        if max_allowed is not None and attrs['amount'] > max_allowed:
            raise serializers.ValidationError(
                "Unable to deposit using the provided amount."
            )

        # Store wallet in attrs so the view can use it without querying again
        attrs['wallet'] = wallet
        return attrs


def _transaction_to_dict(transaction):
    """
    Helper: Convert a Transaction model instance to a JSON-serializable dict.
    We use this when returning transaction data in API responses.
    """
    return {
        'id': transaction.id,
        'amount': str(transaction.amount),
        'currency': transaction.currency,
        'transaction_type': transaction.transaction_type,
        'narration': transaction.narration or '',
        'reference': transaction.reference or '',
        'payment_method': transaction.payment_method or '',
        'created_date': transaction.created_date.isoformat(),
    }
```

**Validation order:**  
1. Field-level (user_id, amount, etc.)  
2. `validate()` for cross-field checks  
3. Only if all pass does the view get `serializer.validated_data`

---

# Part 6: Create the Views (Controllers)

**What is a View?**  
Code that handles a request and returns a response. For APIs, we receive JSON and return JSON.

Open `wallets/views.py` and **replace all content** with:

```python
"""
Views = Controllers. Each view handles one (or more) URL endpoints.
- Receives the HTTP request
- Uses serializers to validate
- Talks to the database via models
- Returns a JSON response
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Transaction, Account, UserWallet
from .serializers import TransactionCreateSerializer, _transaction_to_dict


class TransactionCreateView(APIView):
    """
    Handles POST /api/transactions/create/
    Creates a new transaction and saves it to the database.
    """

    def post(self, request):
        # request.data = the JSON body (e.g. {"user_id": 1, "amount": 100, ...})
        serializer = TransactionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            # Validation failed - return 400 with error messages
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # All valid - validated_data is safe to use
        wallet = serializer.validated_data['wallet']
        transaction = Transaction.objects.create(
            amount=serializer.validated_data['amount'],
            currency=wallet.currency,  # Use wallet's currency (consistent)
            user_wallet=wallet,
            transaction_type=serializer.validated_data['transaction_type'],
            narration=serializer.validated_data.get('narration', ''),
            reference=serializer.validated_data['reference'],
            payment_method=serializer.validated_data.get('payment_method', ''),
        )

        # Return 201 Created with the new transaction as JSON
        return Response(
            {
                'id': transaction.id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'transaction_type': transaction.transaction_type,
                'narration': transaction.narration,
                'reference': transaction.reference,
                'payment_method': transaction.payment_method,
                'created_date': transaction.created_date.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class UserWalletsListView(APIView):
    """
    Handles GET /api/users/<user_id>/wallets/
    Returns all wallets for a user, each with balance and transactions.
    """

    def get(self, request, user_id):
        try:
            account = Account.objects.get(id=user_id, active=True)
        except Account.DoesNotExist:
            return Response(
                {'detail': 'User not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        wallets_data = []
        total_balance = 0

        for wallet in account.wallets.all():  # related_name='wallets' from Account
            balance = wallet.balance  # property we defined on UserWallet
            total_balance += balance
            transactions = [_transaction_to_dict(t) for t in wallet.transactions.all()]
            wallets_data.append({
                'id': wallet.id,
                'name': wallet.name,
                'currency': wallet.currency,
                'description': wallet.description or '',
                'balance': float(balance),
                'transactions': transactions,
            })

        return Response({
            'user_id': account.id,
            'user_name': f'{account.first_name} {account.last_name}',
            'wallets': wallets_data,
            'total_balance': float(total_balance),
        })


class WalletDetailView(APIView):
    """
    Handles GET /api/wallets/<wallet_id>/
    Returns one wallet's balance and all its transactions.
    """

    def get(self, request, wallet_id):
        try:
            wallet = UserWallet.objects.get(id=wallet_id)
        except UserWallet.DoesNotExist:
            return Response(
                {'detail': 'Wallet not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        balance = wallet.balance
        transactions_list = [_transaction_to_dict(t) for t in wallet.transactions.all()]

        return Response({
            'wallet_balance': float(balance),
            'transactions_list': transactions_list,
        })
```

**Flow:**  
Request → `get`/`post` method → Query DB or validate with serializer → Build response dict → `return Response(...)`

---

# Part 7: Wire Up URLs

Django must know which URL leads to which view. We do that in two places.

## Step 7.1 - Create Wallets URLs

Create `wallets/urls.py`:

```python
"""
URL routing for the wallets app.
path('users/<int:user_id>/wallets/', ...) means:
- users/1/wallets/ → user_id=1
- users/42/wallets/ → user_id=42
<int:user_id> = capture the number, pass it to the view as user_id
"""

from django.urls import path
from .views import TransactionCreateView, UserWalletsListView, WalletDetailView

urlpatterns = [
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('users/<int:user_id>/wallets/', UserWalletsListView.as_view(), name='user-wallets'),
    path('wallets/<int:wallet_id>/', WalletDetailView.as_view(), name='wallet-detail'),
]
```

## Step 7.2 - Include in Project URLs

Open `money_tracker/urls.py` and replace with:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('wallets.urls')),  # All wallets URLs get /api/ prefix
]
```

**How it works:**  
A request to `http://127.0.0.1:8000/api/users/1/wallets/` is matched as:
- `api/` → go to `wallets.urls`
- `users/1/wallets/` → `UserWalletsListView` with `user_id=1`

---

# Part 8: Register Models in Admin

Django includes an admin panel. We register our models so we can add/edit data through the browser.

Open `wallets/admin.py` and replace with:

```python
from django.contrib import admin
from .models import Account, UserWallet, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'active', 'created_date')
    list_filter = ('active',)  # Filter sidebar by active/inactive


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'currency', 'created_date')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'amount', 'currency', 'transaction_type', 'payment_method', 'user_wallet', 'created_date')
    list_filter = ('transaction_type', 'currency')
```

**Why:**  
Without this, the admin wouldn’t show our models. `list_display` controls which columns appear in the list view.

---

# Part 9: Create Admin User and Test Data

## Step 9.1 - Create Superuser

```bash
python manage.py createsuperuser
```

This creates a user for the admin panel (separate from our `Account` model). Enter username, email (optional), and password.

## Step 9.2 - Start Server and Add Data

```bash
python manage.py runserver
```

1. Open http://127.0.0.1:8000/admin/
2. Log in with your superuser
3. **Accounts** → Add Account  
   - First name: John, Last name: Doe, Email: john@example.com, Active: ✓
4. **User Wallets** → Add User Wallet  
   - Name: Main Wallet, User: John Doe, Currency: KES, Description: Personal

**Note the IDs:** In the list view or URL, you’ll see something like `/admin/wallets/account/1/`. User ID = 1, Wallet ID = 1 for testing.

---

# Part 10: Test All APIs

Keep the server running. Open a **new** terminal.

## Step 10.1 - Create a Transaction

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/transactions/create/" -Method POST -ContentType "application/json" -Body '{"user_id":1,"amount":500,"transaction_type":"Credit","currency":"KES","narration":"Salary","reference":"TXN-001","payment_method":"M-Pesa"}'
```

**Expected:** JSON with `id`, `amount`, `currency`, etc. Status 201 Created.

**What happened:**  
Request → URLs → `TransactionCreateView.post` → Serializer validated → `Transaction.objects.create` → Response

## Step 10.2 - Get User Wallets

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/users/1/wallets/" -Method GET
```

**Expected:** JSON with `user_id`, `wallets` (each with `balance` and `transactions`), `total_balance`.

## Step 10.3 - Get Wallet Detail

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/wallets/1/" -Method GET
```

**Expected:** JSON with `wallet_balance` and `transactions_list`.

## Step 10.4 - Test Validations

**Duplicate reference (should fail with 400):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/transactions/create/" -Method POST -ContentType "application/json" -Body '{"user_id":1,"amount":100,"transaction_type":"Credit","currency":"KES","narration":"test","reference":"TXN-001","payment_method":""}'
```
Expected: `"A transaction with this reference already exists."`

**Invalid user (should fail with 400):**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/transactions/create/" -Method POST -ContentType "application/json" -Body '{"user_id":999,"amount":100,"transaction_type":"Credit","currency":"KES","narration":"test","reference":"TXN-999","payment_method":""}'
```
Expected: `"Invalid user details provided"`

---

# You're Done!

You’ve built the full flow: **Request → URL → View → Serializer → Model → Database → Response**.

| Component | Role |
|-----------|------|
| **Models** | Define tables and relationships |
| **Serializers** | Validate input and format output |
| **Views** | Handle requests and return responses |
| **URLs** | Map URLs to views |
| **Admin** | Manage data in the browser |

---

# Quick Reference - Project Structure

```
money_tracker_project/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── money_tracker/       (project config)
│   ├── settings.py
│   └── urls.py
└── wallets/             (our app)
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

**Happy learning!**
