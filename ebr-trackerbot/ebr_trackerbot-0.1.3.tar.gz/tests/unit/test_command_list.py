#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

from ebr_trackerbot.command.list import list_command
from ebr_trackerbot.bot import register_storage, config


def test_list_command(test_payload):
    """
    Test list command
    """
    config["storage_backend"] = "test"
    register_storage("test", "save", load_for_user, "load_all", "delete_for_user", "clean_expired_tracks")
    payload = test_payload(post_message_commands)
    text = "list"
    result = "list"
    commands = []
    list_command(text, result, payload, {}, commands)


def post_message_commands(channel, text, thread_ts):
    """
    Check slack message
    """
    assert text == "Tracking for following tests:\n*test* (2100-01-01 00:00:00)\n"
    return {"ok": "ok"}


def load_for_user(user):
    """
    Load record for user
    """
    return [{"test": "test", "expiry": "2100-01-01 00:00:00"}]
