# -*- coding: utf-8 -*-

"""Console messages to the user for quare."""

import click

_ERROR_COLOR = "bright_red"
_ERROR_MSG_COLOR = "magenta"


def _error(msg):
    """Applies default error header style."""
    return click.style(msg, fg=_ERROR_COLOR, bold=True)


# console messages printed via ClickException or Quip*
AUTH_ERROR_MESSAGE = f"""
{_error('Quip says this is an invalid access token.')} To generate a new one to add via `quare auth', visit: https://quip.com/dev/token
"""
TOKEN_ERROR_MESSAGE = f"""
{_error('No default token is set.')} Use `quare auth' or set a QUIP_TOKEN  environment variable containing your authentication token.
"""
MISSING_CONF_ERROR_MESSAGE = f"""{_error('Config is not a file.')} Check your path."""
