import argparse
import logging
import sys

from .environment import VaultEnvironment
from .refresh import VaultTokenRefresher
from .settings import VAULT_ADDR, VAULT_TOKEN

logging.basicConfig()


def process_vault_environment():
    """
    Traverses environment looking for entries to be retrieved from Vault
    """
    sys.exit(VaultEnvironment().run())


def renew_token():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--forever", action="store_true", help="run forever; default false"
    )
    parser.add_argument(
        "--sleep-time",
        type=int,
        default=3600,
        help="how long to sleep between renewals",
    )
    parser.add_argument(
        "--vault-addr",
        default=VAULT_ADDR,
        help="the vault address; defaults to the VAULT_ADDR environment var",
    )
    parser.add_argument(
        "token",
        default=VAULT_TOKEN,
        help="the vault token to renew; defaults to the VAULT_TOKEN environment var",
    )

    args = parser.parse_args()

    refresher = VaultTokenRefresher(
        args.vault_addr, args.token, sleep_time=args.sleep_time, forever=args.forever
    )

    refresher.run()
