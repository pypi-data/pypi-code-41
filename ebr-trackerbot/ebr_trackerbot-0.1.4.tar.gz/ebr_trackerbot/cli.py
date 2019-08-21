# -*- coding: utf-8 -*-

"""Console script for ebr-trackerbot."""
import sys
import argparse

from ebr_trackerbot import bot


def parse_args(args):
    """Returns parsed command line arguments.
    """

    parser = argparse.ArgumentParser(description="Commandline interface for ebr-trackerbot")
    parser.add_argument("--config", type=str, default="config.yaml", help="File path to the configuration.")
    parser.add_argument(
        "--vault_config", type=str, default="vault.yaml", help="File path to the Vault client configuration."
    )
    parser.add_argument(
        "--vault_creds", type=str, default="vault_creds.yaml", help="File path to the Vault credentials."
    )
    return parser.parse_args(args)


def main():
    """Console script for ebr-trackerbot."""
    args = parse_args(sys.argv[1:])
    bot.main(args.config, args.vault_config, args.vault_creds)


if __name__ == "__main__":
    sys.exit(main())
