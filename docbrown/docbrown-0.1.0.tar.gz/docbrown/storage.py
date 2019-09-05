import contextlib
import collections
import datetime
import logging
import sqlite3
from typing import Mapping, Sequence

Timings = Mapping[str, float]
PassedPhase = collections.namedtuple('PassedPhase', ['phase', 'entered_at'])


def _calculate_progress(passed_phases: Sequence[PassedPhase], timings: Timings,
                        now: datetime.datetime):
    expected_duration = sum(timings.values())
    duration = (now - passed_phases[-1].entered_at).total_seconds()

    return {
        'expected_duration': expected_duration,
        'passed_phases': len(passed_phases),
        'expected_phases': len(timings) - 1,
        'current_phase': passed_phases[0].phase,
        'duration': duration,
        'progress': min(100, max(0, duration / expected_duration * 100))
    }


class StorageBackend:
    def store_timings(self, ident, aggregator_key: str, timings: Timings):
        raise NotImplementedError()

    def store_progress(self, ident: str, aggregator_key: str, phase: str,
                       entered_at: datetime.datetime):
        raise NotImplementedError()

    def clear_progress(self, ident: str):
        raise NotImplementedError()

    def get_progress(self, ident: str):
        raise NotImplementedError()


class SQLiteBackend(StorageBackend):
    MIGRATIONS = (
        (
            "CREATE TABLE metadata (meta_key TEXT NOT NULL UNIQUE, "
            "                       meta_value TEXT NOT NULL);",
            "CREATE TABLE timings (aggregator_key TEXT NOT NULL, "
            "                      phase TEXT NOT NULL, "
            "                      duration REAL NOT NULL);",
            "CREATE TABLE progress (ident TEXT NOT NULL, "
            "                       aggregator_key TEXT NOT NULL, "
            "                       phase TEXT NOT NULL, "
            "                       entered_at TEXT NOT NULL);",
        ),
    )

    def __init__(self, db_file):
        self.db_file = db_file
        self._run_migrations()

    @contextlib.contextmanager
    def _cursor(self):
        connection = sqlite3.connect(self.db_file)
        connection.set_trace_callback(logging.debug)
        try:
            yield connection.cursor()
        finally:
            connection.commit()
            connection.close()

    def _run_migrations(self):
        migration_version = None
        with self._cursor() as cursor:
            try:
                cursor.execute('SELECT meta_value FROM metadata WHERE meta_key = "version";')
                version = int(cursor.fetchone()[0])
            except sqlite3.OperationalError:
                version = 0
            for offset, migration in enumerate(self.MIGRATIONS[version:]):
                migration_version = version + offset + 1
                for step in migration:
                    cursor.execute(step)
            if migration_version is not None:
                cursor.execute('REPLACE INTO metadata(meta_key, meta_value) VALUES (?, ?);',
                               ('version', migration_version))

    def store_timings(self, ident, aggregator_key: str, timings: Timings):
        with self._cursor() as cursor:
            for phase, duration in timings.items():
                cursor.execute(
                    'INSERT INTO timings(aggregator_key, phase, duration) VALUES (?, ?, ?);',
                    (aggregator_key, phase, duration))
        self.clear_progress(ident)

    def store_progress(self, ident: str, aggregator_key: str, phase: str,
                       entered_at: datetime.datetime):
        with self._cursor() as cursor:
            cursor.execute('INSERT INTO progress(ident, aggregator_key, phase, entered_at) '
                           'VALUES(?, ?, ?, ?);',
                           [ident, aggregator_key, phase, entered_at.isoformat()])

    def clear_progress(self, ident: str):
        with self._cursor() as cursor:
            cursor.execute('DELETE FROM progress WHERE ident = ?', [ident])

    def get_progress(self, ident):
        now = datetime.datetime.now()

        with self._cursor() as cursor:
            cursor.execute('SELECT aggregator_key, phase, entered_at FROM progress '
                           'WHERE ident = ? ORDER BY entered_at DESC;', [ident])
            passed_phases = cursor.fetchall()
            if len(passed_phases) == 0:
                return None

        aggregator_key = passed_phases[0][0]
        with self._cursor() as cursor:
            cursor.execute('SELECT phase, AVG(duration) AS duration FROM timings '
                           'WHERE aggregator_key = ? GROUP BY phase', [aggregator_key])
            timings = cursor.fetchall()

        timings = {phase: duration for phase, duration in timings}
        passed_phases = [PassedPhase(phase, datetime.datetime.fromisoformat(entered_at))
                         for _, phase, entered_at in passed_phases]
        return _calculate_progress(passed_phases, timings, now)
