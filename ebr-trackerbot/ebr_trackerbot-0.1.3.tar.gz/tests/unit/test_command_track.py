#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

import re
from ebr_trackerbot.command.track import track_command
from ebr_trackerbot.bot import register_storage, get_storage, config


def test_track_command(test_payload):
    """
    Test track command
    """
    config["storage_backend"] = "test"
    register_storage("test", save_record, "load_for_user", "load_all", "delete_for_user", "clean_expired_tracks")
    assert get_storage()["save"] == save_record  # pylint: disable=comparison-with-callable
    payload = test_payload(post_message_commands)
    text = "track test for 10d2h5m10s"
    result = re.match("^track ([^ ]+) for ((?:[0-9]+(?:s|m|h|d))+)$", text, re.IGNORECASE)
    commands = []
    track_command(text, result, payload, {}, commands)


def post_message_commands(channel, text, thread_ts):
    """
    Check slack message when track was successful
    """
    assert re.match(r"^Tracking started for test \*test\* for \*10d2h5m10s\*", text)
    return {"ok": "ok"}


def save_record(user, data):
    """
    Helper function
    """
    return True
