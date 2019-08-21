"""
Slack Bot Generic DB Storage
"""

import logging
import pendulum
import ebr_trackerbot.bot as bot
from functools import partial


def register_storage(name, get_connection):
    """
    Register storage for slackbot
    """
    bot.register_storage(
        name,
        partial(save, get_connection),
        partial(load_for_user, get_connection),
        partial(load_all_tracked_tests, get_connection),
        partial(delete_for_user, get_connection),
        partial(clean_expired_tracks, get_connection),
    )


def create_table(get_connection):
    """
    Create table if it does not exist
    """
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tracks "
            + "(id integer PRIMARY KEY, user text NOT NULL, test text NOT NULL,"
            + " expiry timestamp NOT NULL, channel_id text NOT NULL, thread_ts text NOT NULL)"
        )


def delete_for_user(get_connection, user, test):
    """
    Delete tracking for user and test
    """
    logging.debug("Delete track for user: " + user + ", test: " + test)
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute("DELETE FROM tracks WHERE user = ? AND test = ?", [user, test])


def save(get_connection, user, data):
    """
    Creates tracking for user and test
    """
    logging.debug("Saving track for user: %s, data: ", user)
    logging.debug(data)
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute(
            "SELECT expiry, channel_id, thread_ts FROM tracks WHERE user = ? AND test = ?", [user, data["test"]]
        )
        rows = cursor.fetchall()
        if not rows:
            cursor.execute(
                "INSERT INTO tracks (user, test, expiry, channel_id, thread_ts) VALUES (?, ?, ?, ?, ?)",
                [user, data["test"], data["expiry"], data["channel_id"], data["thread_ts"]],
            )
        else:
            cursor.execute(
                "UPDATE tracks SET expiry = ?, channel_id = ?, thread_ts = ? WHERE user = ? AND test = ?",
                [data["expiry"], data["channel_id"], data["thread_ts"], user, data["test"]],
            )


def load_all_tracked_tests(get_connection):
    """
    Load all tracked tests
    """
    result = []
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute("SELECT user, test, expiry, channel_id, thread_ts FROM tracks")
        rows = cursor.fetchall()
        for row in rows:
            data = {
                "user": row[0],
                "test": row[1],
                "expiry": row[2] if isinstance(row[2], str) else pendulum.instance(row[2]).to_iso8601_string(),
                "channel_id": row[3],
                "thread_ts": row[4],
            }
            result.append(data)
        return result


def load_for_user(get_connection, user):
    """
    Load all tracks for user
    """
    result = []
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute("SELECT user, test, expiry, channel_id, thread_ts FROM tracks WHERE user = ?", [user])
        rows = cursor.fetchall()
        for row in rows:
            data = {
                "test": row[1],
                "expiry": row[2] if isinstance(row[2], str) else pendulum.instance(row[2]).to_iso8601_string(),
                "channel_id": row[3],
                "thread_ts": row[4],
            }
            result.append(data)
        return result


def clean_expired_tracks(get_connection):
    """
    Delete expired tracks
    """
    conn = get_connection()
    cursor = conn.cursor()
    with conn:
        cursor.execute("DELETE FROM tracks WHERE expiry < DATETIME('now')")
