from unittest import TestCase

from vault_tools.uri import SecretURI


class VaultEnvironmentTestCase(TestCase):
    def test_write_env(self):
        uri = SecretURI('secret://vault/path?encode=base64')

        self.assertEquals(True, uri.write_env)

    def test_write_env_with_false_param(self):
        uri = SecretURI('secret://vault/path?encode=base64&write_env=false')

        self.assertEquals(False, uri.write_env)

    def test_write_env_with_true_param(self):
        uri = SecretURI('secret://vault/path?encode=base64&write_env=true')

        self.assertEquals(True, uri.write_env)
