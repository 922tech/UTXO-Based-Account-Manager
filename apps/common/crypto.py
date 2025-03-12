import hashlib
from typing import Any

from cryptography.fernet import Fernet
from django.conf import settings
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError  # FIXME
import binascii
import json


class Encryptor:
    """
    This class abstracts away the encryption algorithm
    """

    def __init__(self, secret=settings.CRYPTO_SECRET):
        self.secret = secret.encode()
        self.__fernet = Fernet(self.secret)

    def encrypt(self, string):
        return self.__fernet.encrypt(string.encode()).decode()

    def decrypt(self, string):
        return self.__fernet.decrypt(string.encode()).decode()


class DigitalSigner:
    _curve = SECP256k1

    def __init__(self, public_key_hex: str, private_key_hex: str = ''):
        """
        Initializes KeyUtil with private and public keys in hexadecimal string format.
        """
        if private_key_hex:
            self._private_key = SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=self._curve)
        self._public_key = VerifyingKey.from_string(binascii.unhexlify(public_key_hex), curve=self._curve)

    def sign(self, value: Any) -> str:
        """
        Signs a string using the private key.
        """
        value = self.serialize(value)
        message_bytes = value.encode('utf-8')
        message_hash = hashlib.sha256(message_bytes).digest()
        signature = self._private_key.sign(message_hash)
        return binascii.hexlify(signature).decode()

    @staticmethod
    def serialize(value):
        return json.dumps(value)

    def verify(self, value, signature_hex):
        """
        Verifies a signature against a value using the public key.
        """
        value = self.serialize(value)
        message_bytes = value.encode('utf-8')
        message_hash = hashlib.sha256(message_bytes).digest()
        try:
            signature_bytes = binascii.unhexlify(signature_hex)
            return self._public_key.verify(signature_bytes, message_hash)

        except (BadSignatureError, binascii.Error) as e:
            return False

    @classmethod
    def generate_key_pair(cls):
        """
        Generates a new key pair.
        """
        private_key = SigningKey.generate(curve=cls._curve)
        public_key = private_key.get_verifying_key()

        return {
            'private': binascii.hexlify(private_key.to_string()).decode(),
            'public': binascii.hexlify(public_key.to_string()).decode(),
        }
