import os

import pytest

from ligo.gracedb.rest import GraceDb


@pytest.fixture
def client():
    """A full client instance for use in integration tests"""
    service_url = os.environ.get(
        'TEST_SERVICE',
        'https://gracedb-test.ligo.org/api/'
    )
    return GraceDb(service_url=service_url)


@pytest.fixture
def test_data_dir():
    d = os.environ.get(
        'TEST_DATA_DIR',
        os.path.join(os.path.dirname(__file__), 'data')
    )
    return d
