# -*- encoding: utf-8 -*-

from flask import current_app, g

from woohoo_pdns import pdns


def init_app(app):
    """Called from the Flask app's :meth:`create_app` and used to register the teardown method (:meth:`close_db`)."""
    app.teardown_appcontext(close_db)


def get_db():
    """Provide access to a single :class:`woohoo_pdns.pdns.Database` for all API endpoints."""
    if 'db' not in g:
        g.db = pdns.Database(current_app.config["DATABASE"])
    return g.db


def close_db(e=None):
    """Close the :class:`woohoo_pdns.pdns.Database` that is present in Flask's global state."""
    db = g.pop('db', None)

    if db is not None:
        db.close()
