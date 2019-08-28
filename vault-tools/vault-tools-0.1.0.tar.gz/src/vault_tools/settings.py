import os

from conversion import convert_bool

# used for the token refresh command
# TODO: switch to vaulthelper for this?
VAULT_ADDR = os.environ.get("VAULT_ADDR")
VAULT_TOKEN = os.environ.get("VAULT_TOKEN")

VAULT_SECRETS_ROOT = os.environ.get('VAULT_SECRETS_ROOT', '/var/run/vault-secrets')
VAULT_WRITE_SECRETS_FILES = convert_bool(os.environ.get('VAULT_WRITE_SECRETS_FILES', 'true'))

