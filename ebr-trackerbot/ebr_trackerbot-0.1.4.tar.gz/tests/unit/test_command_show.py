#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the show command"""

import re
import pendulum
import pytest

from unittest.mock import patch, Mock

from command import show

show_command_inputs = [  # pylint: disable=invalid-name
    ({}, "Something went wrong, please report this failure.", None),
    (
        {"tests": [{"full_name": "bad.not_test", "count": 1}, {"full_name": "some.test", "count": 3}]},
        "Test *{test}* failed {count} times over the last {days}d",
        3,
    ),
    (
        {"tests": [{"full_name": "bad.not_test", "count": 1}, {"full_name": "some.other.test", "count": 3}]},
        "Test *{test}* never failed over {days}d",
        0,
    ),
]


@pytest.mark.parametrize("ebr_board_response, result_text, count", show_command_inputs)
@patch("command.show.requests.get")
def test_show_command_outputs(mock_requests_get, ebr_board_response, result_text, count):
    """
    Test show command outputs
    """
    days = 3
    target_test = "some.test"
    regex_match = "^show ([^ ]+) over ((?:[0-9]+(?:s|m|h|d))+)$"
    command = "show {test} over {days}d".format(days=str(days), test=target_test)
    payload = {"data": {"channel": "test_channel", "ts": 32}}
    config = {"api_url": "test://test.nothing"}

    mock_webclient = Mock()
    payload["web_client"] = mock_webclient

    result = re.match(regex_match, command, re.IGNORECASE)

    mock_requests_get.return_value.json.return_value = ebr_board_response

    time_now = pendulum.now("UTC")
    time_start = time_now.subtract(days=days)

    with patch("command.show.pendulum.now") as mock_pendulum_now:
        mock_pendulum_now.return_value = time_now
        show.show_command("", result, payload, config, "show")

    mock_requests_get.assert_called_once_with(
        "test://test.nothing",
        headers={"accept": "application/json"},
        params={"test_status": "failed", "start": time_start.to_iso8601_string(), "end": time_now.to_iso8601_string()},
    )

    mock_webclient.chat_postMessage.assert_called_once_with(
        channel="test_channel", text=result_text.format(days=days, count=count, test=target_test), thread_ts=32
    )
