# Money Tracker API

A simple Django REST API for users, wallets and transactions.

## Setup (WSL / Ubuntu)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

## Endpoints
Base: `/api/`

- POST `/api/users/` (create user)
- POST `/api/wallets/` (create wallet)
- POST `/api/transactions/create/` (create transaction)
- GET `/api/users/<user_id>/wallets/` (user profile: wallets + balances + total)
- GET `/api/wallets/<wallet_id>/` (wallet details)

## Notes
- Credit adds to balance, Debit subtracts.
- Max amount limits are in `money_tracker/settings.py`.