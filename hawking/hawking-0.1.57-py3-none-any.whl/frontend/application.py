""" Hawking FrontEnd Server.

Copyright (C) 2019 Peach Inc. All rights reserved.
"""
import os
import logging.config

import click

logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)

from flask import Flask, Blueprint
from hawking.frontend.api.search import ns as engine_namespace
from hawking.frontend.api.search import api

blueprint = Blueprint('api', __name__, url_prefix='/api')
api.init_app(blueprint)
api.add_namespace(engine_namespace)

application = Flask(__name__)
application.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
application.config['RESTPLUS_VALIDATE'] = True
application.config['RESTPLUS_MASK_SWAGGER'] = False
application.config['ERROR_404_HELP'] = False
application.register_blueprint(blueprint)


def main(port):
    application.run(host='0.0.0.0', port=port)


@click.command()
@click.option('--port', '-p', help="Listening port", default=8080)
def run(port):
    main(port)


if __name__ == "__main__":
    main(8080)
