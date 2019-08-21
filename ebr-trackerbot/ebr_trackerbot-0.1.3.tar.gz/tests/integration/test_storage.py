#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

import os
import pytest
import tempfile
from ebr_trackerbot import bot


def delete_fixtures():
    """
    Delete sqlite files
    """
    if os.path.exists(tempfile.gettempdir() + "/data.db"):
        os.unlink(tempfile.gettempdir() + "/data.db")
    if os.path.exists(tempfile.gettempdir() + "/data-odbc.db"):
        os.unlink(tempfile.gettempdir() + "/data-odbc.db")


def setup_module():
    """
    Setup environment for tests
    """
    bot.config["odbc_connection_string"] = "DRIVER={SQLITE3};DATABASE=" + tempfile.gettempdir() + "/data-odbc.db"
    delete_fixtures()
    open(tempfile.gettempdir() + "/data-odbc.db", "a").close()


def teardown_module():
    """
    Cleanup
    """
    delete_fixtures()


@pytest.mark.parametrize("module_name", ["odbc", "sqlite"])
def test_storage(module_name):
    """
    Integration test for storage
    """
    module = None
    for storage in bot.STATE.bot_storage:
        if storage["name"] == module_name:
            module = storage
            break
    assert not module["load_all_tracked_tests"]()
    module["save"](
        "test-user", {"test": "abc", "expiry": "2100-01-01T00:00:00Z", "channel_id": "test", "thread_ts": "0123"}
    )
    assert len(module["load_all_tracked_tests"]()) == 1
    assert len(module["load_for_user"]("test-user")) == 1
    assert not module["load_for_user"]("non-existing-user")
    module["delete_for_user"]("test-user", "abc")
    assert not module["load_all_tracked_tests"]()
    assert not module["load_for_user"]("test-user")
    module["save"](
        "test-user", {"test": "abc", "expiry": "2000-01-01T00:00:00Z", "channel_id": "test", "thread_ts": "0123"}
    )
    module["clean_expired_tracks"]()
    assert not module["load_all_tracked_tests"]()
    assert not module["load_for_user"]("test-user")
    module["save"](
        "test-user", {"test": "abc", "expiry": "2000-01-01T00:00:00Z", "channel_id": "test", "thread_ts": "0123"}
    )
    module["save"](
        "test-user", {"test": "abc", "expiry": "2100-01-01T00:00:00Z", "channel_id": "test2", "thread_ts": "01234"}
    )
    assert module["load_for_user"]("test-user")[0]["expiry"] == "2100-01-01T00:00:00Z"
    module["save"](
        "test-user", {"test": "abc2", "expiry": "2100-01-01T00:00:00Z", "channel_id": "test2", "thread_ts": "01234"}
    )
    assert len(module["load_for_user"]("test-user")) == 2
