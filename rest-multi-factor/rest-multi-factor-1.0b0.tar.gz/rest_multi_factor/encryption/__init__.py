"""
Encryption classes.

These classes can be used as a abstract default
way to encrypt or decrypt information.
"""

__all__ = (
    "AESEncryption",
    "AbstractEncryption",
)

from rest_multi_factor.encryption.aes import AESEncryption
from rest_multi_factor.encryption.abstract import AbstractEncryption
