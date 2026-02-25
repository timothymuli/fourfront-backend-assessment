from django.urls import path

from .views import (
    TransactionCreateView,
    UserCreateView,
    UserWalletsListView,
    WalletCreateView,
    WalletDetailView,
)

urlpatterns = [
    path("users/", UserCreateView.as_view(), name="user-create"),
    path("wallets/", WalletCreateView.as_view(), name="wallet-create"),
    path("transactions/create/", TransactionCreateView.as_view(), name="transaction-create"),
    path("users/<int:user_id>/wallets/", UserWalletsListView.as_view(), name="user-wallets"),
    path("wallets/<int:wallet_id>/", WalletDetailView.as_view(), name="wallet-detail"),
]