#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

from ebr_trackerbot.checker import send_track


def test_send_track():
    """
    Check that slack message is send when tests failed in the last period
    """
    track = {}
    track["test"] = "test"
    track["channel_id"] = "test"
    track["thread_ts"] = "test"
    track["user"] = "test"
    count = 1
    check_tests_delay = 7200
    client = type("", (), {})()
    client.chat_postMessage = post_message
    send_track(
        track,
        count,
        check_tests_delay,
        client,
        "Test *{{test}}* failed *{{count}}x* in the last {{period}}\nhttp://test-url?test={{test}}",
    )


def post_message(channel, text, thread_ts):
    """
    Check slack message
    """
    assert text == "Test *test* failed *1x* in the last 2 hours\nhttp://test-url?test=test"


def test_send_track_no_custom_slack_message():
    """
    Check default slack message
    """
    track = {}
    track["test"] = "test"
    track["channel_id"] = "test"
    track["thread_ts"] = "test"
    track["user"] = "test"
    count = 1
    check_tests_delay = 3600
    client = type("", (), {})()
    client.chat_postMessage = post_message_no_custom_slack_message
    send_track(track, count, check_tests_delay, client, None)


def post_message_no_custom_slack_message(channel, text, thread_ts):
    """
    Check slack message
    """
    assert text == ""
