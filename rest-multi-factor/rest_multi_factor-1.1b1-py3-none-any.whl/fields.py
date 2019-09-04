"""Customized django model fields."""

__all__ = (
    "EncryptedField",
)

from django.db.models.fields import CharField

from rest_multi_factor.settings import multi_factor_settings


class EncryptedField(CharField):
    """
    Encrypting field.

    Encrypts the data before inserting it into the
    database and decrypts it on retrieval.
    """

    _encryption = multi_factor_settings.DEFAULT_ENCRYPTION_CLASS()

    def to_python(self, value):
        """
        Decrypt the data from the database.

        :param value: The value to decrypt
        :type value: bytes

        :return: The decrypted data
        :rtype: bytes
        """
        return self._encryption.decrypt(value)

    def from_db_value(self, value, *_):
        """
        Decrypt the data from the database.

        :param value: The value to decrypt
        :type value: bytes | str

        :return: The decrypted data
        :rtype: bytes
        """
        # django 2.x compat
        if isinstance(value, str):  # pragma: no cover
            value = value.encode()

        return self.to_python(value)

    def get_prep_value(self, value):
        """
        Encrypt the data for the database.

        :param value: The value to encrypt
        :type value: bytes

        :return: The encrypted data
        :rtype: bytes
        """
        return self._encryption.encrypt(value).decode()
