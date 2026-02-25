from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Transaction, UserWallet
from .serializers import (
    TransactionCreateSerializer,
    UserCreateSerializer,
    WalletCreateSerializer,
    _transaction_to_dict,
)


class UserCreateView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "phone_number": user.phone_number,
                "active": user.active,
                "created_date": user.created_date.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class WalletCreateView(APIView):
    def post(self, request):
        serializer = WalletCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        wallet = serializer.save()
        return Response(
            {
                "id": wallet.id,
                "user_id": wallet.user_id,
                "name": wallet.name,
                "currency": wallet.currency,
                "description": wallet.description,
                "created_date": wallet.created_date.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class TransactionCreateView(APIView):
    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        wallet = serializer.validated_data["wallet"]
        transaction = Transaction.objects.create(
            amount=serializer.validated_data["amount"],
            currency=wallet.currency,
            user_wallet=wallet,
            transaction_type=serializer.validated_data["transaction_type"],
            narration=serializer.validated_data.get("narration", ""),
            reference=serializer.validated_data["reference"],
            payment_method=serializer.validated_data.get("payment_method", ""),
        )

        return Response(_transaction_to_dict(transaction), status=status.HTTP_201_CREATED)


class UserWalletsListView(APIView):
    def get(self, request, user_id):
        try:
            account = Account.objects.get(id=user_id, active=True)
        except Account.DoesNotExist:
            return Response({"detail": "User not found or inactive."}, status=status.HTTP_404_NOT_FOUND)

        wallets_data = []
        total_balance = 0

        for wallet in account.wallets.all():
            balance = wallet.balance
            total_balance += balance

            wallets_data.append(
                {
                    "id": wallet.id,
                    "name": wallet.name,
                    "currency": wallet.currency,
                    "description": wallet.description or "",
                    "balance": float(balance),
                    "transactions": [_transaction_to_dict(t) for t in wallet.transactions.all()],
                }
            )

        return Response(
            {
                "user_id": account.id,
                "user_name": f"{account.first_name} {account.last_name}",
                "wallets": wallets_data,
                "total_balance": float(total_balance),
            }
        )


class WalletDetailView(APIView):
    def get(self, request, wallet_id):
        try:
            wallet = UserWallet.objects.get(id=wallet_id)
        except UserWallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "wallet_balance": float(wallet.balance),
                "transactions_list": [_transaction_to_dict(t) for t in wallet.transactions.all()],
            }
        )