import contextlib
import datetime
from functools import partial
import os
import uuid
from typing import Callable

from docbrown.storage import StorageBackend, SQLiteBackend

VERSION = '0.1.0'


def _resolve_backend(store):
    if store is None:
        return SQLiteBackend(
            os.path.join(os.path.expanduser('~'), '.python-docbrown.sqlite3'))
    else:
        return store


def _calculate_timings(start, stop, phases):
    phases_seq = list(phases.items())
    result = {}
    for index in range(len(phases)):
        phase_name, start_time = phases_seq[index]
        if index == 0:
            result['__startup__'] = (start_time - start).total_seconds()
        try:
            stop_time = phases_seq[index + 1][1]
        except IndexError:
            stop_time = stop
        result[phase_name] = (stop_time - start_time).total_seconds()
    return result


def _create_recorder(ident: str, store_progress: Callable[[str, datetime.datetime], None]):
    def record(phase_name: str):
        if phase_name in record.passed_phases:
            raise ValueError('already passed phase {}'.format(phase_name))
        now = datetime.datetime.now()
        record.passed_phases[phase_name] = now
        store_progress(phase_name, now)
    record.passed_phases = {}
    record.ident = ident
    return record


@contextlib.contextmanager
def record_progress(aggregator_key: str, ident: str = None, store: StorageBackend = None):
    ident = ident if ident is not None else str(uuid.uuid4())
    store = _resolve_backend(store)
    store.clear_progress(ident)
    store_progress = partial(store.store_progress, ident, aggregator_key)
    recorder = _create_recorder(ident, store_progress)
    start = datetime.datetime.now()
    yield recorder
    stop = datetime.datetime.now()
    store.store_timings(ident, aggregator_key,
                        _calculate_timings(start, stop, recorder.passed_phases))


def get_progress(ident: str, store: StorageBackend = None):
    return _resolve_backend(store).get_progress(ident)
