"""
Tests for the configuration of the trackerbot
"""

from unittest.mock import patch, Mock
import pytest

from ebr_trackerbot import bot


@patch("ebr_trackerbot.bot.VaultAnyConfig")
def test_configure(mock_va):
    """
    Test configuration
    """
    sample_config = {"ebr-trackerbot": {"api_url": "https:/test_url.com", "slack_token": "test-token"}}

    mock_va.return_value.auth_from_file = Mock(return_value=True)
    mock_va.return_value.load = Mock(return_value=sample_config)

    bot.configure("test_config.yaml", "test_vault.yaml", "test_creds.yaml")

    # Validate calls to VaultAnyConfig instance
    mock_va.assert_called_once_with("test_vault.yaml")
    mock_va.return_value.auth_from_file.assert_called_once_with("test_creds.yaml")
    mock_va.return_value.load.assert_called_once_with("test_config.yaml")

    assert bot.config["api_url"] == "https:/test_url.com"
    assert bot.config["slack_token"] == "test-token"
    assert bot.config["check_tests_delay"] == 86400
    assert bot.config["slack_message_template"] == "Test *{{test}}* failed *{{count}}* in the last {{period}}\n"


configs = [  # pylint: disable=invalid-name
    {"ebr-trackerbot": {"slack_token": "test-token"}},
    {"ebr-trackerbot": {"api_url": "http://test_url.com"}},
]


@pytest.mark.parametrize("config", configs)
@patch("ebr_trackerbot.bot.VaultAnyConfig")
def test_fail_missing_api(mock_va, config):
    """
    Test fail missing api
    """
    mock_va.return_value.auth_from_file = Mock(return_value=True)
    mock_va.return_value.load = Mock(return_value=config)

    with pytest.raises(RuntimeError):
        bot.configure("test_config.yaml", "test_vault.yaml", "test_creds.yaml")
