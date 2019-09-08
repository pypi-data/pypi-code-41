"""Custom exceptions for quare and QuipClient"""


class QuipTokenNotFoundError(Exception):
    """
    Thrown if a Quip token is not in the keyring, and the QUIP_TOKEN environment variable is not set."""


class ConfigNotFoundError(Exception):
    """Thrown if a quare config file does not exist."""
