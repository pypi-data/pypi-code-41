#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

from ebr_trackerbot import __version__ as version
from ebr_trackerbot.command.help import help_command


def test_help_empty_command(test_payload):
    """
    Check command output when there are no registered commands
    """
    payload = test_payload(post_message_empty_commands)
    text = "help"
    result = "help"
    commands = []
    help_command(text, result, payload, {}, commands)


def post_message_empty_commands(channel, text, thread_ts):
    """
    Check slack message when there are no registered commands
    """
    assert text == "Hi <@test>!\nI'm EBR-Trackerbot v{version}\nSupported commands:\n".format(version=version)
    return {"ok": "ok"}


def test_help_command(test_payload):
    """
    Check command output where there is one command
    """
    payload = test_payload(post_message_commands)
    text = "help"
    result = "help"
    commands = [{"command": "test", "description": "some description"}]
    help_command(text, result, payload, {}, commands)


def post_message_commands(channel, text, thread_ts):
    """
    Check slack message when there is one command
    """
    assert text == "Hi <@test>!\nI'm EBR-Trackerbot v{version}\nSupported commands:\n*test* some description\n".format(
        version=version
    )
    return {"ok": "ok"}


def test_help_failed_command(test_payload):
    """
    Check behavior when sending slack message failed
    """
    payload = test_payload(post_message_failed_commands)
    text = "help"
    result = "help"
    commands = [{"command": "test", "description": "some description"}]
    help_command(text, result, payload, {}, commands)


def post_message_failed_commands(channel, text, thread_ts):
    """
    Test when something failed
    """
    return {"failed": "failed"}
