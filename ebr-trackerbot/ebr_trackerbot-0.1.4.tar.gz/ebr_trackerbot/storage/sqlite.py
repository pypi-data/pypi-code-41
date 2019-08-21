"""
Slack Bot SQLite Storage
"""

import sqlite3
import logging
import tempfile
from functools import partial
from ebr_trackerbot.storage import db
from ebr_trackerbot.bot import config


def get_connection(configuration):
    """
    Create sqlite connection link
    """
    if get_connection.link is None:
        get_connection.link = sqlite3.connect(configuration.get("sqlite_filename", tempfile.gettempdir() + "/data.db"), check_same_thread=False)
        db.create_table(lambda: get_connection.link)
    return get_connection.link


get_connection.link = None

db.register_storage("sqlite", partial(get_connection, config))
logging.info("SQLite storage registered")
