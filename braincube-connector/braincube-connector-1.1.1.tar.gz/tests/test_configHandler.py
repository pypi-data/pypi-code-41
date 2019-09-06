
# class TestConfigHandler(TestCase):
from braincube.bc_connector.config_handler import is_config_filled


def test_is_config_filled_ko_01():
    assert is_config_filled({"client_secret": "", "client_id": ""}) is False


def test_is_config_filled_ko_02():
    assert is_config_filled({"client_secret": "", "client_id": "test"}) is False


def test_is_config_filled_ko_03():
    assert is_config_filled({"client_secret": "test", "client_id": ""}) is False


def test_is_config_filled_ok():
    assert is_config_filled({"client_secret": "test", "client_id": "test"}) is True
