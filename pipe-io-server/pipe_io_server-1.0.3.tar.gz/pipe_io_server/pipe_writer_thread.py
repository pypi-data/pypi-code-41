# pylint: disable=redefined-builtin
from contextlib import suppress, contextmanager
from os import O_NONBLOCK, O_RDONLY, O_WRONLY, open, close, write, read
from threading import Thread

from .terminate_process_on_failure import terminate_process_on_failure
from .deque import Deque


class PipeWriterThread(Thread):
    def __init__(self, pipe_path, stop_event):
        super().__init__(daemon=True)
        self._pipe_path = pipe_path
        self._write_fd, self._drain_fd = None, None
        self._stop_event = stop_event
        self._write_queue = Deque()

    def write(self, message):
        self._write_queue.push(message)

    @terminate_process_on_failure
    def run(self):
        with self._open():
            while True:
                message = self._write_queue.pop()
                if message is None:
                    self._stop_event.set()
                    break
                write(self._write_fd, message + b'\n')

    @contextmanager
    def _open(self):
        self._drain_fd = open(self._pipe_path, O_RDONLY | O_NONBLOCK)
        self._write_fd = open(self._pipe_path, O_WRONLY)
        yield
        close(self._write_fd)
        close(self._drain_fd)

    def stop(self):
        while self.is_alive():
            self._unblock()
        self.join()

    def _unblock(self):
        self._write_queue.push_front(None)
        with suppress(OSError, TypeError):
            while read(self._drain_fd, 65536):
                pass
