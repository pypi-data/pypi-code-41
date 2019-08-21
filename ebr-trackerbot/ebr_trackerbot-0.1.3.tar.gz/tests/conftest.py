"""
Common functions for tests
"""

import pytest


@pytest.fixture
def test_payload():
    """
    Retrieve test payload
    """

    def _test_payload(post_message):
        payload = {}
        payload["web_client"] = type("", (), {})()
        payload["web_client"].chat_postMessage = post_message
        payload["data"] = {}
        payload["data"]["user"] = "test"
        payload["data"]["channel"] = "test"
        payload["data"]["ts"] = "test"
        return payload

    return _test_payload
