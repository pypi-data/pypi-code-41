#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ebr_trackerbot` package."""

import logging
import pytest
import ebr_trackerbot.storage.db
from unittest.mock import Mock


def test_storage_db_create_table():
    """
    Test table creation
    """
    conn = Mock()
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None

    ebr_trackerbot.storage.db.create_table(lambda: conn)

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_called_once_with(
        "CREATE TABLE IF NOT EXISTS tracks"
        + " (id integer PRIMARY KEY, user text NOT NULL, test text NOT NULL,"
        + " expiry timestamp NOT NULL, channel_id text NOT NULL, thread_ts text NOT NULL)"
    )


def test_storage_db_create_table_exception(caplog):
    """
    Test table creation when something failed
    """
    conn = Mock()
    conn.cursor.side_effect = Mock(side_effect=Exception("TestException"))

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception):
            ebr_trackerbot.storage.db.create_table(lambda: conn)


def test_storage_db_delete_for_user():
    """
    Test record deletion for user and test
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock

    ebr_trackerbot.storage.db.delete_for_user(lambda: conn, "test-user", "test")

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_called_once_with(
        "DELETE FROM tracks WHERE user = ? AND test = ?", ["test-user", "test"]
    )


def test_storage_db_save_no_existing_record():
    """
    Test save record - insert
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock
    execute_mock.fetchall.return_value = []

    ebr_trackerbot.storage.db.save(
        lambda: conn,
        "test-user",
        {"test": "test", "expiry": "expiry", "channel_id": "channel_id", "thread_ts": "thread_ts"},
    )

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_any_call(
        "SELECT expiry, channel_id, thread_ts FROM tracks WHERE user = ? AND test = ?", ["test-user", "test"]
    )
    execute_mock.execute.assert_any_call(
        "INSERT INTO tracks (user, test, expiry, channel_id, thread_ts) VALUES (?, ?, ?, ?, ?)",
        ["test-user", "test", "expiry", "channel_id", "thread_ts"],
    )


def test_storage_db_save_existing_record():
    """
    Test save record - update
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock
    execute_mock.fetchall.return_value = ["some record"]

    ebr_trackerbot.storage.db.save(
        lambda: conn,
        "test-user",
        {"test": "test", "expiry": "expiry", "channel_id": "channel_id", "thread_ts": "thread_ts"},
    )

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_any_call(
        "SELECT expiry, channel_id, thread_ts FROM tracks WHERE user = ? AND test = ?", ["test-user", "test"]
    )
    execute_mock.execute.assert_any_call(
        "UPDATE tracks SET expiry = ?, channel_id = ?, thread_ts = ? WHERE user = ? AND test = ?",
        ["expiry", "channel_id", "thread_ts", "test-user", "test"],
    )


def test_storage_db_load_all_tracked_tests():
    """
    Test load all records
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock
    records = [
        ["test-user", "test", "expiry", "channel_id", "thread_ts"],
        ["test-user2", "test2", "expiry2", "channel_id2", "thread_ts2"],
    ]
    execute_mock.fetchall.return_value = records

    assert ebr_trackerbot.storage.db.load_all_tracked_tests(lambda: conn) == [
        {"user": "test-user", "test": "test", "expiry": "expiry", "channel_id": "channel_id", "thread_ts": "thread_ts"},
        {
            "user": "test-user2",
            "test": "test2",
            "expiry": "expiry2",
            "channel_id": "channel_id2",
            "thread_ts": "thread_ts2",
        },
    ]

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_called_once_with("SELECT user, test, expiry, channel_id, thread_ts FROM tracks")


def test_storage_db_load_for_user():
    """
    Test load all records for user
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock
    execute_mock.fetchall.return_value = [["test-user", "test", "expiry", "channel_id", "thread_ts"]]

    assert ebr_trackerbot.storage.db.load_for_user(lambda: conn, "test-user") == [
        {"test": "test", "expiry": "expiry", "channel_id": "channel_id", "thread_ts": "thread_ts"}
    ]

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_called_once_with(
        "SELECT user, test, expiry, channel_id, thread_ts FROM tracks WHERE user = ?", ["test-user"]
    )


def test_storage_db_clean_expired_tracks():
    """
    Test clean expired records
    """
    conn = Mock()
    conn.__enter__ = lambda _: None
    conn.__exit__ = lambda a, b, c, d: None
    execute_mock = Mock()
    conn.cursor.return_value = execute_mock

    ebr_trackerbot.storage.db.clean_expired_tracks(lambda: conn)

    conn.cursor.assert_called_once()
    execute_mock.execute.assert_called_once_with("DELETE FROM tracks WHERE expiry < DATETIME('now')")
