"""Models for the ing app."""
from __future__ import annotations

from typing import Dict, List

from django.db import models
from django_cryptography.fields import encrypt


class UpdateOrCreateFromJsonMixin:
    """Add helper functions to allow easy creation of models from json data."""

    update_or_create_kwargs: List[str]
    json_field_mapping: Dict[str, str]

    @classmethod
    def get_update_or_create_kwargs(cls):
        """Return the update_or_create kwargs."""
        assert hasattr(cls, "update_or_create_kwargs"), (
            f"'{cls.__name__}' should either include a `update_or_create_kwargs`"
            " attribute, or override the `get_update_or_create_kwargs()` method."
        )
        return getattr(cls, "update_or_create_kwargs")

    @classmethod
    def get_json_mapping(cls):
        """Return the mapping of json key -> field key."""
        assert hasattr(cls, "json_field_mapping"), (
            f"'{cls.__name__}' should either include a `json_field_mapping`"
            " attribute, or override the `get_json_mapping()` method."
        )
        return getattr(cls, "json_field_mapping")

    @classmethod
    def json_to_field_mapping(cls, json_data):
        """Return the json data mapped to the model's fields."""
        return {
            field_key: json_data[json_key]
            for json_key, field_key in cls.get_json_mapping().items()
        }

    @classmethod
    def update_or_create_from_json(cls, json_data, **kwargs):
        """Update or create the instance from the json data."""
        defaults = {}
        update_kwargs = {}
        update_or_create_kwargs = cls.get_update_or_create_kwargs()
        for key, value in {**cls.json_to_field_mapping(json_data), **kwargs}.items():
            if key in update_or_create_kwargs:
                update_kwargs[key] = value
            else:
                defaults[key] = value
        return cls._default_manager.update_or_create(**update_kwargs, defaults=defaults)


class Credentials(models.Model):
    """Store the encrypted credentials."""

    pin = encrypt(models.CharField(max_length=8))


class Client(UpdateOrCreateFromJsonMixin, models.Model):
    """Store information about ING clients."""

    cif = models.CharField(max_length=10)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    salutation = models.CharField(max_length=10)

    credentials = models.ForeignKey(
        to=Credentials, on_delete=models.SET_NULL, null=True, blank=True
    )

    update_or_create_kwargs = ["cif"]
    json_field_mapping = {
        "FirstName": "first_name",
        "LastName": "last_name",
        "MiddleName": "middle_name",
        "Salutation": "salutation",
    }

    class JSONAPIMeta:
        """JSON:API meta information."""

        resource_name = "clients"


class Account(UpdateOrCreateFromJsonMixin, models.Model):
    """Store information about ING accounts."""

    number = models.CharField(max_length=8)
    name = models.CharField(max_length=60)
    available_balance = models.DecimalField(max_digits=14, decimal_places=2)
    owner = models.ForeignKey(to=Client, on_delete=models.CASCADE)

    update_or_create_kwargs = ["owner", "number"]
    json_field_mapping = {
        "AccountNumber": "number",
        "AccountName": "name",
        "AvailableBalance": "available_balance",
    }

    class JSONAPIMeta:
        """JSON:API meta information."""

        resource_name = "accounts"


class Transaction(UpdateOrCreateFromJsonMixin, models.Model):
    """Store information about ING transactions."""

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_date = models.DateTimeField()
    extended_description = models.CharField(max_length=200)
    receipt_number = models.CharField(max_length=10)
    transaction_id = models.IntegerField(unique=True)
    transaction_type = models.IntegerField()
    transaction_group = models.CharField(max_length=20)
    account = models.ForeignKey(to=Account, on_delete=models.CASCADE)

    update_or_create_kwargs = ["transaction_id"]
    json_field_mapping = {
        "Amount": "amount",
        "TransactionDate": "transaction_date",
        "ExtendedDescription": "extended_description",
        "ReceiptNumber": "receipt_number",
        "TransactionId": "transaction_id",
        "TransactionType": "transaction_type",
        "TransactionGroup": "transaction_group",
    }

    class JSONAPIMeta:
        """JSON:API meta information."""

        resource_name = "transactions"
