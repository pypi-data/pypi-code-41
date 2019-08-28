import logging
import os

from google.auth.exceptions import DefaultCredentialsError
import google.cloud.logging as gl
from google.cloud.logging.handlers.handlers import EXCLUDED_LOGGER_DEFAULTS
from google.cloud.logging.resource import Resource

from .app import cli
import sentry_sdk


client = sentry_sdk.init(
    'https://f695d7ce05f143b393d6dfc84d1b723f@sentry.io/1335287',
    environment=os.environ.get('ML_SOCKET_SERVER_ENVIRONMENT'),
    release=os.environ.get('ML_SOCKET_SERVER_VERSION'))

log_format = '%(asctime)s %(levelname)-8s: %(message)s'
if os.environ.get('DEBUG', False):
    log_format = '%(asctime)s %(levelname)-8s [%(name)s.%(funcName)s:%(lineno)d]: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt='%m-%d %H:%M:%S')

root = logging.getLogger()

for handler in root.handlers:
    handler.setLevel(logging.DEBUG if os.environ.get('DEBUG', False) else logging.INFO)
    for logger_name in EXCLUDED_LOGGER_DEFAULTS:
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        logger.addHandler(handler)

try:
    gl_client = gl.Client()
    cloud_handler = gl_client.get_default_handler(
        resource=Resource(
            type='gce_instance',
            labels={"instance_id": os.environ.get('HOSTNAME'), "zone": "None"}
        )
    )
    cloud_handler.setLevel(logging.DEBUG)
    cloud_log_format = '[%(name)s.%(funcName)s:%(lineno)d]: %(message)s'
    fmt = logging.Formatter(cloud_log_format)
    cloud_handler.setFormatter(fmt)
    root.addHandler(cloud_handler)
except DefaultCredentialsError:
    root.exception('Failed to init cloud logging')


def main():
    cli()


if __name__ == "__main__":
    main()
