from django.conf import settings
from rest_framework import serializers

from .models import Account, Transaction, UserWallet


class UserCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.CharField(max_length=60)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)

    def create(self, validated_data):
        return Account.objects.create(**validated_data)


class WalletCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    name = serializers.CharField(max_length=20)
    currency = serializers.CharField(max_length=3)
    description = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_user_id(self, value):
        if not Account.objects.filter(id=value, active=True).exists():
            raise serializers.ValidationError("Invalid user details provided")
        return value

    def validate_currency(self, value):
        value = (value or "").upper()
        if value not in ["KES", "USD"]:
            raise serializers.ValidationError("Currency must be KES or USD")
        return value

    def validate(self, attrs):
        if UserWallet.objects.filter(user_id=attrs["user_id"], currency=attrs["currency"]).exists():
            raise serializers.ValidationError("Wallet already exists for this user and currency")
        return attrs

    def create(self, validated_data):
        user = Account.objects.get(id=validated_data["user_id"], active=True)
        return UserWallet.objects.create(
            user=user,
            name=validated_data["name"],
            currency=validated_data["currency"],
            description=validated_data.get("description", ""),
        )


class TransactionCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)
    transaction_type = serializers.ChoiceField(choices=["Credit", "Debit"], required=True)
    currency = serializers.CharField(max_length=10, required=True)
    narration = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reference = serializers.CharField(max_length=100, required=True)
    payment_method = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_user_id(self, value):
        if not Account.objects.filter(id=value, active=True).exists():
            raise serializers.ValidationError("Invalid user details provided")
        return value

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Invalid amount provided")
        return value

    def validate_reference(self, value):
        if Transaction.objects.filter(reference=value).exists():
            raise serializers.ValidationError("A transaction with this reference already exists.")
        return value

    def validate(self, attrs):
        user_id = attrs["user_id"]
        currency = (attrs.get("currency") or "").upper()

        try:
            wallet = UserWallet.objects.get(user_id=user_id, currency=currency)
        except UserWallet.DoesNotExist:
            raise serializers.ValidationError("Unable to deposit funds in the provided wallet")

        max_allowed = getattr(settings, "MAXIMUM_AMOUNTS", {}).get(currency)
        if max_allowed is not None and attrs["amount"] > max_allowed:
            raise serializers.ValidationError("Unable to deposit using the provided amount.")

        attrs["wallet"] = wallet
        return attrs


def _transaction_to_dict(transaction):
    return {
        "id": transaction.id,
        "amount": str(transaction.amount),
        "currency": transaction.currency,
        "transaction_type": transaction.transaction_type,
        "narration": transaction.narration or "",
        "reference": transaction.reference or "",
        "payment_method": transaction.payment_method or "",
        "created_date": transaction.created_date.isoformat(),
    }