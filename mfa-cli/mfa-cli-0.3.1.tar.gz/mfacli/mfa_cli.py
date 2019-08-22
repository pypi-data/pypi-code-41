# -*- coding: utf-8 -*-
"""Cli entrypoint for mfa_cli

This modules use click (https://click.palletsprojects.com/en/7.x/) to manage
cli args for mfa_cli.

Example:
    $ python -m mfa_cli list-keys --keyfile codes.yml
    $ python -m mfa_cli new-totp --keyfile codes.yml
    $ python -m mfa_cli new-totp --keyfile codes.yml --keyname myservice

Todo:
    * Use pyAesCrypt for keyfile encryption
"""

__version__ = "0.3.1"

from datetime import datetime

import click

import pyperclip

from .manage_totp import TOTP

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# yapf: disable
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__)
def main():
    """CLI tool for generating one-time passwords."""


# yapf: enable
@main.command()
@click.option('-kf',
              '--keyfile',
              type=click.Path(exists=True),
              required=True,
              help='YAML file with service keys')
@click.option('-kn', '--keyname', help='keyname to generate a new totp')
def new_totp(keyname, keyfile):
    """Generate a new key based totp for a service"""
    totp = TOTP(keyfile)
    if not keyname:
        print("No key selected, select a key from the list:")
        keyname = totp.choose_one_key()
    totp_now = totp.get_new_totp(keyname)
    remaining_time = 30 - (datetime.now().second % 30)
    try:
        pyperclip.copy(totp_now)
        if pyperclip.is_available():
            pyperclip.copy(totp_now)
            print("\n{} otp: {}\nValid for: {} seconds\n"
                  "It is available on your clipboard.".format(
                      keyname, totp_now, remaining_time))
    except pyperclip.PyperclipException:
        print("\n{} otp: {}\nValid for: {} seconds\n".format(
            keyname, totp_now, remaining_time))
        print("Consider installing xclip/xsel to export"
              " your totp to clipboard")


@main.command()
@click.option('-kf',
              '--keyfile',
              type=click.Path(exists=True),
              required=True,
              help='YAML file with service keys')
def list_keys(keyfile):
    """
    List all keys from a key file


    Parameters:
        keyfile: path to file containing all service keys
    """
    totp = TOTP(keyfile)
    totp.list_keys()


if __name__ == '__main__':
    main()
