"""Serializers for ing app."""
from rest_framework_json_api import serializers

from ing import models


class ClientSerializer(serializers.Serializer):
    """Serializer for Client."""

    cif = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    middle_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    salutation = serializers.CharField(read_only=True)

    class Meta:
        """Serializer meta information."""

        model = models.Client

    def create(self, validated_data):
        """Not implemented."""
        raise NotImplementedError("This is a read only serializer")

    def update(self, instance, validated_data):
        """Not implemented."""
        raise NotImplementedError("This is a read only serializer")


class AccountSerializer(serializers.Serializer):
    """Serializer for Account."""

    number = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    available_balance = serializers.DecimalField(
        read_only=True, max_digits=14, decimal_places=2
    )
    owner = serializers.ResourceRelatedField(model=models.Client, read_only=True)

    class Meta:
        """Serializer meta information."""

        model = models.Account

    def create(self, validated_data):
        """Not implemented."""
        raise NotImplementedError("This is a read only serializer")

    def update(self, instance, validated_data):
        """Not implemented."""
        raise NotImplementedError("This is a read only serializer")


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction."""

    class Meta:
        """Serializer meta information."""

        model = models.Transaction
        read_only_fields = [
            "amount",
            "transaction_date",
            "extended_description",
            "receipt_number",
            "transaction_id",
            "transaction_type",
            "transaction_group",
            "account",
        ]
        fields = read_only_fields
