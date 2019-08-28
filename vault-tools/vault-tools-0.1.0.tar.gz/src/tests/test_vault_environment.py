from unittest import TestCase

from vault_tools.environment import VaultEnvironment
from vault_tools.uri import SecretURI


class VaultEnvironmentTestCase(TestCase):
    def test_base64_encoding(self):
        uri = SecretURI('secret://vault/path?encode=base64')
        vault_environment = VaultEnvironment()

        encoded = vault_environment.get_encoded(uri, 'test')

        self.assertEquals('base64://dGVzdA==', encoded)

    def test_json_encoding(self):
        uri = SecretURI('secret://vault/path?encode=json')
        vault_environment = VaultEnvironment()

        encoded = vault_environment.get_encoded(uri, 'test')

        self.assertEquals('json://"test"', encoded)

    def test_no_encoding(self):
        uri = SecretURI('secret://vault/path')
        vault_environment = VaultEnvironment()

        encoded = vault_environment.get_encoded(uri, 'test')

        self.assertEquals('test', encoded)
