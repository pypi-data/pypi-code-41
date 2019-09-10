# -*- coding: utf-8 -*-
"""
    flest
    ~~~~~

    Flest - small contribution to Flask world.
    The goal is to help spend less time typing and coding and do more.

    :copyright: 2019 Jihwan Song
    :license: MIT License
"""
from flask import *
from ._self import (
            Flest, declare_blueprint,
            FlestResponse, HTMLResponse, JSONResponse, RawResponse,
            RedirectResponse, 
            HTMLResponse as Template, RawResponse as Raw,
            JSONResponse as AJAX, RedirectResponse as Redirect
        )

from .decorators import get_only, public
from .config import Config

# load them if installed
# TODO: allow not loading them if instructed in configuration
try:
    from flask_socketio import SocketIO
except Exception:
    pass


__version__ = '0.1.26'
