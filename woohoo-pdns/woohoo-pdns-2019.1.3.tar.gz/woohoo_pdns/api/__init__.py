# -*- encoding: utf-8 -*-

import os, sys

from flask import Flask


def create_app(test_config=None):
    """A Flask specific method that is called automagically."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("woohoo_pdns.api.config.DefaultSettings")
    app.config.from_envvar("WOOHOO_PDNS_API_SETTINGS", silent=False)

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)
    from . import api
    app.register_blueprint(api.bp)

    return app
