"""Helper class to handle ING api requests."""
import base64
import json

import requests
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as cipher_method
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from common.utils import ocr

BASE_URL = "https://www.ing.com.au"


class IngApi:
    """Class for interacting with ING's api."""

    auth_header = "X-AuthToken"
    signature_header = "X-MessageSignature"

    def __init__(self, cif: str):
        """Initialise the various instance variables."""
        super().__init__()
        self.cif = cif
        self.key = self.generate_rsa_key()
        self.public_modulus = hex(self.key.n)[2:]
        self.token = ""
        self.b64images = None
        self.secret = None
        self.server_key = None

    def init_login_request(self):
        """Get the keyboard mapping from ING."""
        url = f"{BASE_URL}/KeypadService/v1/KeypadService.svc/json/PinpadImages"
        response = requests.get(url=url)
        json_response = response.json()
        self.b64images = json_response["KeypadImages"]
        self.secret = json_response["Secret"]
        self.server_key = RSA.importKey(json_response["PemEncryptionKey"])

    @classmethod
    def generate_rsa_key(cls):
        """Generate a new RSA keypair."""
        rng = Random.new().read
        return RSA.generate(1024, rng)

    def get_signature(self, body=None):
        """Sign request."""
        digest = SHA.new()
        message = f"{self.auth_header}:".encode("utf-8")
        message += self.token.encode("utf-8")
        if body is not None:
            message += json.dumps(body).encode("utf-8")
        digest.update(message)
        signer = PKCS1_v1_5.new(self.key)
        return signer.sign(digest).hex()

    def images_to_dict(self):
        """Convert the b64images to a dict from the image number to index."""
        return {
            ocr.b64_image_to_int(image): index
            for index, image in enumerate(self.b64images)
        }

    def get_encrypted_pin(self, pin) -> str:
        """Get the encrypted pin."""
        image_mapping = self.images_to_dict()
        mapped = ",".join([str(image_mapping[digit]) for digit in pin]).encode("utf-8")
        cipher = cipher_method.new(self.server_key)
        return base64.b64encode(cipher.encrypt(mapped)).decode("utf-8")

    def make_request(
        self, *, path: str, body=None, headers=None, add_auth=True, sign_message=True
    ):
        """Make a request to the ING api."""
        body = {} if body is None else body
        headers = {} if headers is None else headers
        path = path[1:] if path.startswith("/") else path
        if add_auth:
            headers[self.auth_header] = self.token
        if sign_message:
            headers[self.signature_header] = self.get_signature(body)
        return requests.post(f"{BASE_URL}/{path}", headers=headers, json=body)

    def login(self, pin):
        """Log into ING."""
        self.init_login_request()
        headers = {
            "X-AuthPIN": self.get_encrypted_pin(pin),
            "X-AuthCIF": self.cif,
            "X-MessageSignKey": self.public_modulus,
            "X-AuthSecret": self.secret,
        }
        response = self.make_request(
            path="/STSServiceB2C/V1/SecurityTokenServiceProxy.svc/issue",
            headers=headers,
        )
        response_json = response.json()
        if not response_json["ErrorMessage"]:
            self.token = response_json["Token"]
        return response

    def get_account_details(self, account_number, page_size=1):
        """Get account details from the ING api."""
        body = {
            "PageSize": page_size,
            "PageNumber": 0,
            "AccountNumber": account_number,
        }
        response = self.make_request(
            path=(
                "/api/AccountDetails/Service/AccountDetailsService.svc"
                "/json/accountdetails/AccountDetails"
            ),
            body=body,
        )
        return response

    def get_account_transactions(
        self, account_number, page_size=25, page_number=0, search_query=""
    ):
        """Get account transactions."""
        body = {
            "PageSize": page_size,
            "PageNumber": page_number,
            "SearchQuery": search_query,
            "AccountNumber": account_number,
        }
        response = self.make_request(
            path=(
                "/api/TransactionHistory/Service/TransactionHistoryService.svc"
                "/json/TransactionHistory/TransactionHistory"
            ),
            body=body,
        )
        return response

    def get_dashboard(self):
        """Get account transactions."""
        response = self.make_request(
            path=(
                "/api/Dashboard/Service/DashboardService.svc"
                "/json/Dashboard/loaddashboard"
            ),
            body={},
        )
        return response
