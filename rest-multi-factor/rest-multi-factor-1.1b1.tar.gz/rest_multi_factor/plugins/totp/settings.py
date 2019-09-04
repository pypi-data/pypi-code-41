"""Additional, plugin-specific settings."""

__all__ = (
    "DEFAULTS",
    "LOADABLE",
)

DEFAULTS = {
    "TOTP_DIGITS": 6,
    "TOTP_PERIOD": 30,
    "TOTP_ISSUER": "rest-multi-factor",

    "TOTP_TOLERANCE": 2,
    "TOTP_ALGORITHM": "hashlib.sha1",
}

LOADABLE = [
    "TOTP_ALGORITHM",
]

