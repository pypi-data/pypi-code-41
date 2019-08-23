# -*- coding: utf-8 -*-

"""
Main module for the app. Can either use the create_app or invoke through command line to start the application.
"""
from flask import Flask, Blueprint
from flask_restplus import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from config import VaultConfig

from api.job.job import ns as job_namespace
from api.job.build.build import ns as job_build_namespace
from api.job.build.test.tests import ns as job_build_test_namespace
from api.tests import ns as tests_namespace
from models import ns as models_namespace

from __init__ import __version__, __project__


def create_app(  # pylint: disable=too-many-arguments
    config="config.yaml",
    vault_config="vault.yaml",
    vault_creds="vault.yaml",
    config_format=None,
    load_certs=False,
    reverse_proxy=True,
):
    """
    Args:
        config{str} -- [File path to configuration or a string containing the configuration] (default: {'config.yaml'})
        vault_config {str} -- [File path to configuration or a string containing the configuration] (default: {'vault.yaml'})
        vault_creds {str} -- [File path to configuration or a string containing the configuration](default: {'vault.yaml'})
        load_certs {bool} -- Automatically load certificate and key files during configuration (default: {False})
        config_format {str} -- Specifies the parser to use when reading the configuration, only needed if reading a string. See the ac_parser option
            in python-anyconfig for available formats. Common ones are `json` and `yaml`.
    """

    config = VaultConfig(config, vault_config, vault_creds, config_format=config_format, load_certs=load_certs)

    app = Flask(__name__)  # pylint: disable=invalid-name
    app.config.from_object(config)

    api_bp = Blueprint("api", __name__, url_prefix="/api")
    configure_api(api_bp)

    with app.app_context():
        register_blueprints(app, api_bp)

    if reverse_proxy:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

    return app


def register_blueprints(app, api_bp):
    """
    Args:
        app {[type]} -- [description]
    """
    app.register_blueprint(api_bp)


def configure_api(api_bp):
    """
    Handles the configuration of the API
    """
    ebr_board_api = Api(  # pylint: disable=invalid-name
        version=__version__,
        title="{project} JSON API".format(project=__project__),
        description="JSON API for the EBR dashboard",
        doc="/docs",
    )
    ebr_board_api.add_namespace(job_namespace)
    ebr_board_api.add_namespace(job_build_namespace)
    ebr_board_api.add_namespace(job_build_test_namespace)
    ebr_board_api.add_namespace(tests_namespace)
    ebr_board_api.add_namespace(models_namespace)

    ebr_board_api.init_app(api_bp)


if __name__ == "__main__":
    create_app(config="config.yaml", vault_config="vault.yaml", vault_creds="vault.yaml", load_certs=True).run(
        debug=True
    )
