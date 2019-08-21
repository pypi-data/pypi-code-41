"""
Slack Bot ODBC Storage
"""

import pyodbc
import logging
from ebr_trackerbot.bot import config
from ebr_trackerbot.storage import db
from functools import partial


def create_connection(configuration):
    """
    Create odbc connection link
    """
    if configuration.get("odbc_connection_string") is None:
        raise RuntimeError("Missing odbc_connection_string in configuration")
    link = pyodbc.connect(configuration.get("odbc_connection_string"))
    db.create_table(lambda: link)
    return link


def get_connection(configuration):
    """
    Retrieve odbc connection
    """
    if get_connection.link is None:
        get_connection.link = create_connection(configuration)
    return get_connection.link


get_connection.link = None

db.register_storage("odbc", partial(get_connection, config))
logging.info("ODBC storage registered")
