# -*- encoding: utf-8 -*-


class DefaultSettings(object):
    """The default configuration of the API just demonstrates the available options."""
    SECRET_KEY="snakeoil"
    """Flask uses a secret key to encrypt things that sould be tamper proof (for example the Session object)."""
    DATABASE="sqlite:///demo.db"
    """The connection string to be used by SQLAlchemy."""
    API_KEYS=[
        "IXsA7uRnxR4xek4JDEG5vk2oGjTYDSqaoKLRQLVjV2s3kw0bbv49qrgAT7Bk3g2K",
        "jLHKK0AIk1l6r3W8SAJj4Lh0v2a27JGbSSd406mr0u5FNrJn6RLWQ5m6qPYXT0d5",
        ]
    """The complete list of available/valid API keys."""
