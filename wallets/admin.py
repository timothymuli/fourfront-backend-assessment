from django.contrib import admin
from .models import Account, UserWallet, Transaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'active', 'created_date')
    list_filter = ('active',)


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'currency', 'created_date')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'amount', 'currency', 'transaction_type', 'payment_method', 'user_wallet', 'created_date')
    list_filter = ('transaction_type', 'currency')
