from .server_django import patch as patch_django
from .server_flask import patch as patch_flask
from .client_requests import patch as patch_requests
from .client_urllib_request import patch as patch_urllib_request
from .client_kombu import patch as patch_kombu
from .app_celery import patch as patch_celery
from .testing_unittest import patch as patch_unittest
from .testing_pytest import patch as patch_pytest
from .logging_logging import patch as patch_logging
from .sql.psycopg2 import install_patches as patch_psycopg2


def patch_all():
    patch_django()
    patch_flask()
    patch_requests()
    patch_urllib_request()
    patch_kombu()
    patch_celery()
    patch_unittest()
    patch_pytest()
    patch_logging()
    patch_psycopg2()
