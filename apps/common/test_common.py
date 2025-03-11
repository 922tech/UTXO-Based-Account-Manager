"""
This module contains the logic for testing common utils.
"""
from apps.common.tests import BaseTestCase

import binascii
import json
from django.test import TestCase
from cryptography.fernet import Fernet, InvalidToken
from apps.common.crypto import Encryptor, DigitalSigner  # Update with the actual module path


class EncryptorTest(BaseTestCase):
    def setUp(self):
        self.secret = Fernet.generate_key().decode()
        self.encryptor = Encryptor(secret=self.secret)

    def test_encryption_decryption(self):
        """Test that encryption and decryption work correctly"""
        plaintext = "hello world"
        encrypted = self.encryptor.encrypt(plaintext)
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertNotEqual(plaintext, encrypted)  # Ensure it's actually encrypted
        self.assertEqual(decrypted, plaintext)  # Ensure it decrypts correctly

    def test_decryption_with_wrong_key_fails(self):
        """Test that decryption with a different key raises an error"""
        wrong_encryptor = Encryptor(secret=Fernet.generate_key().decode())
        plaintext = "test message"
        encrypted = self.encryptor.encrypt(plaintext)

        with self.assertRaises(InvalidToken):
            wrong_encryptor.decrypt(encrypted)


class DigitalSignerTest(TestCase):
    def setUp(self):
        self.key_pair = DigitalSigner.generate_key_pair()
        self.signer = DigitalSigner(
            private_key_hex=self.key_pair["private"],
            public_key_hex=self.key_pair["public"]
        )

    def test_sign_and_verify(self):
        """Test that signing and verification work correctly"""
        message = "hello world"
        signature = self.signer.sign(message)
        self.assertTrue(self.signer.verify(message, signature))

    def test_verify_invalid_signature_fails(self):
        """Test that an invalid signature is rejected"""
        message = "hello world"
        invalid_signature = "00" * 64  # An obviously fake signature
        self.assertFalse(self.signer.verify(message, invalid_signature))

    def test_generate_key_pair_creates_valid_keys(self):
        """Test that the generated key pair works for signing and verification"""
        key_pair = DigitalSigner.generate_key_pair()
        signer = DigitalSigner(
            private_key_hex=key_pair["private"],
            public_key_hex=key_pair["public"]
        )
        message = "blockchain message"
        signature = signer.sign(message)
        self.assertTrue(signer.verify(message, signature))

    def test_serialization_consistency(self):
        """Test that serialization produces consistent results"""
        value = {"key": "value"}
        serialized = self.signer.serialize(value)
        self.assertEqual(serialized, json.dumps(value))

    def test_invalid_private_key_raises_error(self):
        """Test that an invalid private key raises an error on initialization"""
        with self.assertRaises(binascii.Error):
            DigitalSigner(public_key_hex=self.key_pair["public"], private_key_hex="invalid_private_key")
