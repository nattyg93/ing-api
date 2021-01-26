"""Management Command to setup initial data."""
import math
from typing import List

from django.core.management.base import BaseCommand

from ing import models
from ing.api import IngApi


class Command(BaseCommand):
    """Management command to import account information."""

    def add_arguments(self, parser):
        """Add parser arguments."""

        def int_list(raw: str) -> List[int]:
            """Convert string to list of int digits."""
            return [int(digit) for digit in str(raw)]

        parser.add_argument(
            "--cif", type=str, required=True, help="ING cif - client number"
        )
        parser.add_argument("--pin", type=int_list, required=True, help="ING PIN")

    def handle(self, *args, **options):
        """Run the management command."""
        api = IngApi(cif=options["cif"])
        # Try to log in
        login_json = api.login(pin=options["pin"]).json()
        if not login_json["ErrorMessage"]:
            self.stdout.write("Successfully logged in")
        else:
            self.stdout.write("Could not log in with the credentials provided")
            return
        # Try to get the dashboard info
        dashboard_json = api.get_dashboard().json()
        if not dashboard_json["Result"]:
            self.stdout.write("No result from loading dashboard")
            return
        self.stdout.write("Creating client")
        # Sync client info from the dashboard response
        client = models.Client.update_or_create_from_json(
            dashboard_json["Response"]["Client"], cif=options["cif"]
        )[0]
        accounts = []
        # Sync account info from the dashboard response
        for category in dashboard_json["Response"]["Categories"]:
            for account in category["Accounts"]:
                accounts.append(
                    models.Account.update_or_create_from_json(account, owner=client)[0]
                )
        # Sync all transactions info for all accounts
        for account in accounts:
            page_size = 200
            page_number = 0
            while True:
                transactions_json = api.get_account_transactions(
                    account.number, page_size=page_size, page_number=page_number
                ).json()
                if not transactions_json["Result"]:
                    self.stdout.write(
                        "No result from loading transactions with: "
                        f"account_number={account.number}, page_size={page_size}, "
                        f"page_number={page_number}",
                    )
                    return
                for transaction_json in transactions_json["Response"]["Transactions"]:
                    models.Transaction.update_or_create_from_json(
                        transaction_json, account=account
                    )
                # Calculate if all pages have been retrieved
                total_pages = math.ceil(
                    transactions_json["Response"]["TotalTransactionsCount"]
                    / float(page_size)
                )
                if page_number + 1 >= total_pages:
                    break
                page_number += 1
