"""Abstract Encryption class for general purposes."""


__all__ = (
    "AbstractEncryption",
)


from abc import ABCMeta, abstractmethod


class AbstractEncryption(metaclass=ABCMeta):
    """
    Abstract Encryption Handler.

    This class is used to ensure that regardless of what encryption
    method is applied.
    """

    @property
    @abstractmethod
    def key(self):
        """
        Key to use for the encryption/decryption.

        :return: The key to use
        :rtype: bytes
        """

    @abstractmethod
    def encrypt(self, secret):
        """
        Encrypt a secret.

        :param secret: The secret to encrypt
        :type secret: bytes

        :return: The encrypted value to store
        :rtype: bytes
        """

    @abstractmethod
    def decrypt(self, stored):
        """
        Decrypt the stored value to retrieve the secret.

        :param stored: The encrypted stored value to decrypt
        :type stored: bytes

        :return: The decrypted secret
        :rtype: bytes
        """
