import base64
import json
import logging
import os

from functools import lru_cache

import vaulthelpers

from .settings import VAULT_SECRETS_ROOT, VAULT_WRITE_SECRETS_FILES
from .uri import SecretURI


class VaultEnvironment:
    """
    Traverses the OS environment looking for values that should be fetched from Vault
    """
    def __init__(self,
                 secrets_root: str = VAULT_SECRETS_ROOT,
                 write_secrets_files: bool = VAULT_WRITE_SECRETS_FILES):
        self.write_secrets_files = write_secrets_files
        self.secrets_root = secrets_root

    def _check_item(self, key: str, value: str):
        """
        Processes the environment variable at the name `key` with the given value

        look for environment values such as secret://vault/secret/something
        """
        uri = SecretURI(value)
        if not uri.is_secret:
            return

        secret = self.get_secret(uri)

        self.write_secret_file(key, secret)
        self.update_env(uri, key, secret)

    @property
    @lru_cache()
    def client(self):
        return vaulthelpers.client()

    def get_secret(self, uri: SecretURI):
        """
        Returns the secret found in Vault for the given secret URI
        """
        vault_response = self.client.secrets.kv.v2.read_secret_version(path=uri.path)

        return vault_response['data'][uri.key]

    @property
    def logger(self):
        return logging.getLogger('{}.{}'.format(__name__, self.__class__.__name__))

    def run(self):
        if not self.client:
            # the vaulthelpers client function will warn already
            # self.logger.warning('Vault not configured; cannot fetch secrets')

            return

        for k, v in os.environ.items():
            self._check_item(k, v)

    @staticmethod
    def get_encoded(uri: SecretURI, value: str) -> str:
        """
        Returns the value encoded per the uri settings

        Args:
        uri: the variable URI
        value: the value to encode

        Returns:
            the encoded value
        """
        encoded = value

        encode = uri.encode
        if encode == 'base64':
            encoded = base64.b64encode(value.encode('utf8')).decode('utf8')
        elif encode == 'json':
            encoded = json.dumps(value)
        elif encode is not None:
            raise ValueError('Unknown encoding: {}'.format(encode))

        return '{}://{}'.format(encode, encoded) if encode else encoded

    def update_env(self, uri: SecretURI, key: str, value: str) -> None:
        """
        Python cannot update the parent environment, so what this does is print it to stdout

        The parent process is responsible for taking stdout and updating the runtime environment
        """
        # if the individual secret has opeted to not update the environment, skip printing
        if not uri.write_env:
            return

        encoded = self.get_encoded(uri, value)

        print('{}={}'.format(key, encoded))

    def write_secret_file(self, key: str, value: str) -> None:
        """
        Write the secret to a file in the secrets root directory
        """
        if not self.write_secrets_files:
            return

        # make the directory here instead of in a constructor so that an empty directory isn't left
        # behind if nothing is found
        if not os.path.exists(self.secrets_root):
            os.makedirs(self.secrets_root)

        full_path = os.path.join(self.secrets_root, key)
        with open(full_path, 'w') as fh:
            fh.write(value)
