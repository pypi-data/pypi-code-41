"""Test Session functionality with Batfish service backend."""
from os.path import abspath, dirname, join, realpath

import pytest

from pybfe.client.session import Session

_this_dir = abspath(dirname(realpath(__file__)))


@pytest.fixture()
def session():
    return Session()


@pytest.fixture()
def snapshot(session):
    name = session.init_snapshot(join(_this_dir, 'snapshots', 'basic'))
    yield name
    session.delete_snapshot(name)


def test_validate_facts(session, snapshot):
    """Confirm fact validation returns the expected dictionary of mismatched facts."""
    validation_results = session.validate_facts(
        expected_facts=join(_this_dir, 'facts', 'basic_fail'))

    assert validation_results == {
        'basic': {
            'Syslog.Logging_Servers': {
                'actual': [],
                'expected': ['1.2.3.5'],
            },
            'Extra_Key': {
                'expected': 'something',
                'key_present': False,
            }
        }
    }, 'Logging_Servers should be different and Extra_Key should be missing'
