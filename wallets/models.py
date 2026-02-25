from django.db import models


class Account(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=60)
    phone_number = models.CharField(max_length=15, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserWallet(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="wallets")
    description = models.CharField(max_length=50, blank=True)
    currency = models.CharField(max_length=3)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_wallets"
        ordering = ["-created_date"]
        unique_together = [["user", "currency"]]

    def __str__(self):
        return f"{self.name} ({self.currency})"

    @property
    def balance(self):
        total = 0
        for txn in self.transactions.all():
            if txn.transaction_type == "Credit":
                total += txn.amount
            else:
                total -= txn.amount
        return total


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("Credit", "Credit"),
        ("Debit", "Debit"),
    ]

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10)
    user_wallet = models.ForeignKey(UserWallet, on_delete=models.CASCADE, related_name="transactions")
    created_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    narration = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.currency}"