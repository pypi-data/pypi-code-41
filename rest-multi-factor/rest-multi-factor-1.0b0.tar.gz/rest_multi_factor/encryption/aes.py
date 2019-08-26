"""AES Encryption implementation (including a Fernet suit)."""


__all__ = (
    "AESEncryption",
)


import base64
import hashlib


from django.conf import settings

from cryptography.fernet import Fernet


from rest_multi_factor.encryption.abstract import AbstractEncryption


class AESEncryption(AbstractEncryption):
    """
    AES Encryption implementation.

    This implementation is basically a proxy
    to cryptography's Fernet suit.
    """

    @property
    def key(self):
        """
        Key to use for encryption/ decryption.

        By default the django SECRET_KEY is used.

        The SECRET_KEY is hashed with MD5 to get a 32-byte
        string, because that's required by AES encryption.

        :return: The key to use
        :rtype: bytes
        """
        digest = hashlib.md5(settings.SECRET_KEY.encode())
        return base64.urlsafe_b64encode(digest.hexdigest().encode())

    def encrypt(self, secret):
        """
        Encrypt the secret.

        Encrypt the secret with AES encryption and Fernet suit.

        :param secret: The secret to encrypt
        :type secret: bytes

        :return: The encrypted value
        :rtype: bytes
        """
        return Fernet(self.key).encrypt(secret)

    def decrypt(self, stored):
        """
        Decrypt the secret.

        Decrypt the secret with AES encryption and Fernet suit.

        :param stored: The value to decrypt
        :type stored: bytes

        :return: The decrypted value
        :rtype: bytes
        """
        return Fernet(self.key).decrypt(stored)
