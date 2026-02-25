"""
Serializers for Money Tracker API.
"""

from rest_framework import serializers
from django.conf import settings

from .models import Transaction, Account, UserWallet


class TransactionCreateSerializer(serializers.Serializer):
    """
    Serializer for api/transactions/create endpoint.
    Validates request body per Solution.xlsx.
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
    reference = serializers.CharField(max_length=100, required=True)  # Unique per transaction
    payment_method = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_user_id(self, value):
        """Validate user exists and is active."""
        try:
            account = Account.objects.get(id=value, active=True)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Invalid user details provided")
        return value

    def validate_amount(self, value):
        """Amount must be positive."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Invalid amount provided")
        return value

    def validate_transaction_type(self, value):
        """Must be Credit or Debit."""
        if value not in ['Credit', 'Debit']:
            raise serializers.ValidationError(
                "Transaction type must be Credit or Debit"
            )
        return value

    def validate_reference(self, value):
        """Reference must be unique across all transactions."""
        if Transaction.objects.filter(reference=value).exists():
            raise serializers.ValidationError(
                "A transaction with this reference already exists."
            )
        return value

    def validate(self, attrs):
        """Cross-field validation: user must have wallet with given currency."""
        user_id = attrs['user_id']
        currency = attrs.get('currency', '').upper()

        currency_upper = currency.upper()
        try:
            wallet = UserWallet.objects.get(user_id=user_id, currency=currency_upper)
        except UserWallet.DoesNotExist:
            raise serializers.ValidationError(
                "Unable to deposit funds in the provided wallet"
            )

        # Validate max amount per currency (from App Configurations)
        max_amounts = getattr(settings, 'MAXIMUM_AMOUNTS', {})
        max_allowed = max_amounts.get(currency_upper)
        if max_allowed is not None and attrs['amount'] > max_allowed:
            raise serializers.ValidationError(
                "Unable to deposit using the provided amount."
            )

        attrs['wallet'] = wallet
        return attrs


def _transaction_to_dict(transaction):
    """Helper to format a Transaction for API response."""
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
