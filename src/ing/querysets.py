"""QuerySets for ing app."""
from __future__ import annotations

from django.db.models import QuerySet


class ClientQuerySet(QuerySet):
    """QuerySet for Client model."""

    def for_user(self, user):
        """Filter to only clients owned by the user."""
        return self.filter(user=user)


class AccountQuerySet(QuerySet):
    """QuerySet for Account model."""

    def for_user(self, user):
        """Filter to only accounts owned by the user."""
        return self.filter(owner__user=user)


class TransactionQuerySet(QuerySet):
    """QuerySet for Transaction model."""

    def for_user(self, user):
        """Filter to only transactions owned by the user."""
        return self.filter(account__owner__user=user)
