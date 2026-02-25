"""
URL routes for wallets app.
"""

from django.urls import path
from .views import TransactionCreateView, UserWalletsListView, WalletDetailView

urlpatterns = [
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('users/<int:user_id>/wallets/', UserWalletsListView.as_view(), name='user-wallets'),
    path('wallets/<int:wallet_id>/', WalletDetailView.as_view(), name='wallet-detail'),
]
