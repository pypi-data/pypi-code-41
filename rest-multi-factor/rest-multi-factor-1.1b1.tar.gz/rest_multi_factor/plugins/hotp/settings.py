"""Additional, plugin-specific settings."""

__all__ = (
    "DEFAULTS",
    "LOADABLE",
)

DEFAULTS = {
    "HOTP_DIGITS": 6,
    "HOTP_ISSUER": "rest-multi-factor",

    "HOTP_TOLERANCE": 2,
    "HOTP_ALGORITHM": "hashlib.sha1",
}

LOADABLE = [
    "HOTP_ALGORITHM",
]

