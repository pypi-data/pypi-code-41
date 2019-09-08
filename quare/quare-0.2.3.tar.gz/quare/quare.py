# -*- coding: utf-8 -*-
"""Contains business logic for interactions with the Quip API."""

import os

import keyring
import terminaltables

from quare import quip, ui_messages
from quare.exceptions import QuipTokenNotFoundError
from quare.quip_classes import QuipFolder

SVC_NAME = "quare"
TOKEN_ENV_VAR = "QUIP_TOKEN"  # nosec


def get_user_token(alias="Default"):
    """Retreive an api token from the keyring or environment variable.

    Keyword args:
    alias -- the alias under which the token is stored (default "Default")
    """
    token = keyring.get_password(SVC_NAME, alias)
    if type(token) is str:
        return alias, token
    elif TOKEN_ENV_VAR in os.environ and os.environ[TOKEN_ENV_VAR]:
        return alias, os.environ[TOKEN_ENV_VAR]
    else:
        raise QuipTokenNotFoundError(ui_messages.TOKEN_ERROR_MESSAGE)


def set_user_token(alias, token):
    """Store an API token and associated metadata."""
    keyring.set_password(SVC_NAME, alias, token)


def get_user_info(token, alias="User"):
    """Call the Quip API and get information about the authenticated user.

    Keyword args:
    alias -- the alias under which the token is stored (default "Default")
    """
    client = quip.QuipClient(token)
    user = client.get_authenticated_user()
    table = terminaltables.SingleTable(_format_user_matrix(user), alias)
    table.inner_row_border = True
    return user, table.table


def send_messages(token, alias, room):
    """Call the Quip API and send a message."""
    client = quip.QuipClient(token)
    messages = client.send_messages(room)
    return messages


def _format_user_matrix(user):
    """Given a Quip user dict, return a matrix that terminal tables will accept."""
    return [
        ["Name", user["name"]],
        ["Email(s)", ", ".join(user["emails"]) if "emails" in user else ""],
        ["Quip User ID", user["id"]],
    ]


def _get_user_favorites(user, token):
    """Given a user dict, recursively retrieve the user's starred items."""
    starred_id = user["starred_folder_id"]
    client = quip.QuipClient(token)
    folder = client.get_folder(starred_id)
    print(folder)
    folder = QuipFolder(**folder)
    return _get_children(folder, token)


def _get_children(folder, token):
    """Get all child threads for this folder."""
    client = quip.QuipClient(token)
    threads = client.get_threads(folder.child_threads)
    return threads
