"""
API views for Money Tracker.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Transaction, Account, UserWallet
from .serializers import TransactionCreateSerializer, _transaction_to_dict


class TransactionCreateView(APIView):
    """
    api/transactions/create - Create a new transaction.
    Validations per Solution.xlsx:
    - User exists and is active
    - User has wallet with given currency (UserId + Currency)
    - Amount > 0
    - Amount <= max for currency (KES: 10000, USD: 10000)
    - Transaction type: Credit or Debit
    """

    def post(self, request):
        serializer = TransactionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        wallet = serializer.validated_data['wallet']
        transaction = Transaction.objects.create(
            amount=serializer.validated_data['amount'],
            currency=wallet.currency,  # Use wallet's currency for consistency
            user_wallet=wallet,
            transaction_type=serializer.validated_data['transaction_type'],
            narration=serializer.validated_data.get('narration', ''),
            reference=serializer.validated_data['reference'],
            payment_method=serializer.validated_data.get('payment_method', ''),
        )

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
    GET /api/users/<user_id>/wallets/
    Get all wallets for a user with balance (Credits - Debits) and transactions per wallet.
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

        for wallet in account.wallets.all():
            balance = wallet.balance
            total_balance += balance
            transactions = [
                _transaction_to_dict(t) for t in wallet.transactions.all()
            ]
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
    GET /api/wallets/<wallet_id>/
    Get individual wallet details: balance and all transactions for the wallet.
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
        transactions_list = [
            _transaction_to_dict(t) for t in wallet.transactions.all()
        ]

        return Response({
            'wallet_balance': float(balance),
            'transactions_list': transactions_list,
        })
