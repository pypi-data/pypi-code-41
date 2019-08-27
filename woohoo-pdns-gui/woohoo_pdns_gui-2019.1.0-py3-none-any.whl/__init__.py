# -*- encoding: utf-8 -*-

import os, sys

from werkzeug.exceptions import NotFound
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask


def no_app(environ, start_response):
    return NotFound()(environ, start_response)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("woohoo_pdns_gui.config.DefaultSettings")
    app.config.from_envvar("WOOHOO_PDNS_GUI_SETTINGS", silent=False)
    app.wsgi_app = DispatcherMiddleware(no_app, {app.config["WOOHOO_APPLICATION_ROOT"]: app.wsgi_app})

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import app as a
    app.register_blueprint(a.bp)

    return app
