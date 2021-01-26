"""Views for the ing app."""
from rest_framework import permissions
from rest_framework_json_api import views

from common.views import AuthorisedQuerySetMixin
from ing import models, serializers


class ClientView(AuthorisedQuerySetMixin, views.ReadOnlyModelViewSet):
    """clients endpoint."""

    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["pk"]


class AccountView(AuthorisedQuerySetMixin, views.ReadOnlyModelViewSet):
    """accounts endpoint."""

    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["pk"]


class TransactionView(AuthorisedQuerySetMixin, views.ReadOnlyModelViewSet):
    """transactions endpoint."""

    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ["pk"]
