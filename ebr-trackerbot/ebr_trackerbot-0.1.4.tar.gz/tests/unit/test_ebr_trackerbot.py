#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

import pytest
import logging
from unittest.mock import Mock, patch
import ebr_trackerbot.bot as bot


@pytest.fixture
def message_event_payload():
    """
    Provides a message event payload
    """

    return {
        "data": {
            "type": "message",
            "client_msg_id": "1654564.546",
            "channel": "test_channel",
            "user": "test_sending_user",
            "text": "list",
            "ts": "1654654.0546",
        }
    }


def test_register_command():
    """Register command test"""
    bot.register_command("test", "description", "regex", "callback")
    assert "test" in map(lambda x: x["command"], bot.STATE.bot_command)


def test_register_storage():
    """Register storage test"""
    bot.register_storage("test", "save", "load_for_user", "load_all", "delete_for_user", "clean_expired_tracks")
    assert "test" in map(lambda x: x["name"], bot.STATE.bot_storage)


def test_get_storage():
    """Get storage test"""
    bot.register_storage("test", "save", "load_for_user", "load_all", "delete_for_user", "clean_expired_tracks")
    bot.config["storage_backend"] = "test"
    assert "save" in bot.get_storage()
    assert bot.get_storage()["save"] == "save"


def test_slack_message_listener_incomplete_payload(caplog):
    """
    Tests the slack_message_listener to ensure it logs a debug message if a field is missing from the data it is passed
    """
    payload = {"data": {"type": "message"}}
    with caplog.at_level(logging.DEBUG):
        bot.slack_message_listener("test_user", {}, **payload)
    assert "Missing one of: channel, ts, user, client_msg_id in slack message" in caplog.text


def test_slack_message_listener_no_user_mentioned(
    caplog, message_event_payload
):  # pylint: disable=redefined-outer-name
    """
    Tests the slack_message_listener to ensure it logs a debug message if there is no bot user "at mentioned" nor has it been direct messaged
    """
    with caplog.at_level(logging.DEBUG):
        bot.slack_message_listener("test_user", {}, **message_event_payload)
    assert 'Message does not "at mention" bot username' in caplog.text


@patch("bot.STATE", autospec=False)
def test_slack_message_listener_user_mentioned(caplog, message_event_payload):  # pylint: disable=redefined-outer-name
    """
    Tests the slack_message_listener to ensure it processes the command when the slackbot user is "at mentioned"
    """
    bot_user = "test-user"
    payload = message_event_payload

    # Provide @mention for message
    payload["data"]["text"] = "<@{user}> bad_command".format(user=bot_user)
    payload["data"]["client_msg_id"] = "123455"
    mock_web_client = Mock()
    payload["web_client"] = mock_web_client

    bot.slack_message_listener(bot_user, {}, **payload)

    mock_web_client.chat_postMessage.assert_called_once_with(
        channel=payload["data"]["channel"],
        text="Hi <@{user}>! \nI don't understand your command. Please type *help* to see all supported commands\n".format(
            user=payload["data"]["user"]
        ),
        thread_ts=payload["data"]["ts"],
    )


@patch("bot.STATE", autospec=False)
def test_slack_message_listener_direct_message(caplog, message_event_payload):  # pylint: disable=redefined-outer-name
    """
    Tests the slack_message_listener to ensure it processes the command when the slackbot user is sent a direct message
    """
    bot_user = "test_user"
    payload = message_event_payload

    # Provide proper channel format
    payload["data"]["channel"] = "Dchannel_name"
    payload["data"]["client_msg_id"] = "123456"
    payload["data"]["text"] = "unknown"
    mock_web_client = Mock()
    payload["web_client"] = mock_web_client

    bot.slack_message_listener(bot_user, {}, **payload)

    mock_web_client.chat_postMessage.assert_called_once_with(
        channel=payload["data"]["channel"],
        text="Hi <@{user}>! \nI don't understand your command. Please type *help* to see all supported commands\n".format(
            user=payload["data"]["user"]
        ),
        thread_ts=payload["data"]["ts"],
    )


def test_slack_message_listener_skip_same_messages(caplog):
    """
    Tests the slack_message_listener
    """
    bot_user = "test_user"
    payload = {
        "data": {
            "type": "message",
            "client_msg_id": "1654564.546",
            "channel": "test_channel",
            "user": "test_sending_user",
            "text": "list",
            "ts": "1654654.0547",
        }
    }

    with caplog.at_level(logging.DEBUG):
        for _ in range(20):
            bot.slack_message_listener(bot_user, {}, **payload)
        assert len(caplog.records) == 20
        for record in caplog.records:
            assert record.msg == "Message already processed"


def test_slack_message_listener_keep_last_10_messages():
    """
    Tests the slack_message_listener
    """
    bot_user = "test_user"
    payload = {
        "data": {
            "type": "message",
            "client_msg_id": "1654564.546",
            "channel": "test_channel",
            "user": "test_sending_user",
            "text": "bla",
            "ts": "1654654.0547",
        }
    }

    for i in range(20):
        payload["data"]["client_msg_id"] = "123" + str(i)
        bot.slack_message_listener(bot_user, {}, **payload)
    assert len(bot.STATE.last_msgs) == 10


def test_slack_message_listener_update_wrapper():
    """
    Tests that update_wrapper is correctly preserving __name__
    """

    assert bot.get_partial_function(bot.slack_message_listener).__name__ == "slack_message_listener"
