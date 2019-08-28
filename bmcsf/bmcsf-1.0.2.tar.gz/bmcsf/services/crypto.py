import os

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend


class CryptoService:
    def get_public_key(self):
        if not self._has_ssh_keys():
            keys = self._generate_ssh_keys()
            self._dump_keys(*keys)

        return self._read_key_file()

    def get_private_key(self):
        if not self._has_ssh_keys():
            keys = self._generate_ssh_keys()
            self._dump_keys(*keys)

        return self._read_key_file('private')

    def _read_key_file(self, key_type='public'):
        key_path = self._get_public_key_path()
        if 'private' == key_type:
            key_path = self._get_private_key_path()

        f = open(key_path, 'r')
        lines = f.readlines()
        f.close()

        return "".join(lines)

    def _dump_keys(self, private_key, public_key):
        f = open(self._get_public_key_path(), 'w')
        f.write(public_key)
        f.close()

        f = open(self._get_private_key_path(), 'w')
        f.write(private_key)
        f.close()

    def _has_ssh_keys(self):
        return os.path.isfile(
            self._get_public_key_path()
        ) and os.path.isfile(
            self._get_private_key_path()
        )

    @staticmethod
    def _get_base_path():
        return os.path.join(
            os.path.expanduser('~'),
            '.ssh'
        )

    def _get_public_key_path(self):
        return os.path.join(
            self._get_base_path(),
            'id_rsa.pub'
        )

    def _get_private_key_path(self):
        return os.path.join(
            self._get_base_path(),
            'id_rsa'
        )

    @staticmethod
    def _generate_ssh_keys():
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )

        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption()
        ).decode('ascii')

        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        ).decode('ascii')

        return private_key, public_key
