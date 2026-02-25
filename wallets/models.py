"""
Money Tracker models per Solution.xlsx
- Account (Users table)
- UserWallet
- Transaction
"""

from django.db import models


class Account(models.Model):
    """
    Users table - represents a user account (no auth required).
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=15, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserWallet(models.Model):
    """
    UserWallets table - a wallet (account) belonging to a user.
    User can have multiple wallets, e.g. for different businesses.
    """
    name = models.CharField(max_length=20)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='wallets')
    description = models.CharField(max_length=50, blank=True)  # e.g. Wallet Name
    currency = models.CharField(max_length=3)  # e.g. KES, USD
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_wallets'
        ordering = ['-created_date']
        # User can have only one wallet per currency
        unique_together = [['user', 'currency']]

    def __str__(self):
        return f"{self.name} ({self.currency})"

    @property
    def balance(self):
        """Calculate wallet balance: Income (Credit) adds, Expense (Debit) subtracts."""
        total = 0
        for txn in self.transactions.all():
            if txn.transaction_type == 'Credit':
                total += txn.amount
            else:  # Debit
                total -= txn.amount
        return total


class Transaction(models.Model):
    """
    Transactions table - income (Credit) or expense (Debit) for a wallet.
    """
    TRANSACTION_TYPES = [
        ('Credit', 'Credit'),  # Income
        ('Debit', 'Debit'),    # Expense
    ]

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10)
    user_wallet = models.ForeignKey(
        UserWallet, on_delete=models.CASCADE, related_name='transactions'
    )
    created_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    narration = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Unique per transaction (null allowed for legacy rows)
    payment_method = models.CharField(max_length=50, blank=True)  # e.g. M-Pesa, Bank Transfer, Card

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency}"
