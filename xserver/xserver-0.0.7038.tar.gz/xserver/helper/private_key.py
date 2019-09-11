#coding: utf8
from __future__ import absolute_import
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


def create_private_public_keys_for_ssh():
    private_key = rsa.generate_private_key(
         public_exponent=65537,
         key_size=4096,
         backend=default_backend()
    )
    public_key = private_key.public_key()
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL, #PKCS8, .TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    return private_key_bytes, public_key_bytes