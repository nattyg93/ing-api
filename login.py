#!/usr/bin/env python
"""Log into ING."""

import argparse
import base64
import json
from io import BytesIO

import requests
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as cipher_method
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "https://www.ing.com.au"


def get_arguments():
    """Parse and return the arguments passed on the cli."""
    parser = argparse.ArgumentParser(description="Login via the ING Api")
    parser.add_argument("cif", type=str, help="ING cif - client number")
    return vars(parser.parse_args())


class IngApi:
    """Class for interacting with ING's api."""

    def __init__(self, cif: str):
        """Initialise the various instance variables."""
        self.cif = cif
        self.key = self.generate_rsa_key()
        self.public_modulus = hex(self.key.n)[2:]
        self.token = None
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
        message = b"X-AuthToken:"
        if self.token:
            message += self.token.encode("utf-8")
        if body is not None:
            message += json.dumps(body).encode("utf-8")
        digest.update(message)
        signer = PKCS1_v1_5.new(self.key)
        return signer.sign(digest).hex()

    def show_keypad(self):
        """Get and show keyboard image."""
        img = Image.new("RGB", (180 * 3, 110 * 4))
        index = 0
        skipped = False
        font = ImageFont.truetype("Arcon-Regular.otf", size=22)
        for y_coord in range(0, 110 * 4, 110):
            for x_coord in range(0, 180 * 3, 180):
                if index == 9 and not skipped:
                    skipped = True
                    continue
                if index < 10:
                    image = Image.open(BytesIO(base64.b64decode(self.b64images[index])))
                    draw = ImageDraw.Draw(image)
                    draw.text((0, 0), str(index), font=font)
                    index = index + 1
                    img.paste(image, (x_coord, y_coord))
        img.show()

    def get_encrypted_pin(self) -> str:
        """Get the encrypted pin."""
        self.show_keypad()
        key_position = input("enter comma separated keypad positions: ").encode("utf-8")
        cipher = cipher_method.new(self.server_key)
        return base64.b64encode(cipher.encrypt(key_position)).decode("utf-8")

    def login(self):
        """Log into ING."""
        self.init_login_request()
        headers = {
            "X-AuthPIN": self.get_encrypted_pin(),
            "X-AuthCIF": self.cif,
            "X-MessageSignKey": self.public_modulus,
            "X-AuthToken": "",
            "X-AuthSecret": self.secret,
            "X-AuthSignature": self.get_signature(),
        }
        return requests.post(
            url=f"{BASE_URL}/STSServiceB2C/V1/SecurityTokenServiceProxy.svc/issue",
            headers=headers,
            json={},
        )


def main():
    """Run the thing."""
    args = get_arguments()
    api = IngApi(args["cif"])
    response = api.login()
    print(response.json())


if __name__ == "__main__":
    main()
