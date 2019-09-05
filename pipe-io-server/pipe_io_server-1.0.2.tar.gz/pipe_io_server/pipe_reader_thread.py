# pylint: disable=redefined-builtin,too-many-instance-attributes
from contextlib import contextmanager
from os import O_NONBLOCK, O_RDONLY, O_WRONLY, open, fdopen, close, write, pipe
from threading import Thread
from select import select

from .terminate_process_on_failure import terminate_process_on_failure


class PipeReaderThread(Thread):
    def __init__(self, pipe_path, stop_event, message_handler):
        super().__init__(daemon=True)
        self._message_handler = message_handler
        self._pipe_path = pipe_path
        self._read_fd, self._read_fp, self._prevent_eof_fd = None, None, None
        self._stop_signal_rfd, self._stop_signal_wfd = pipe()
        self._msg_buf = b''
        self._stop_event = stop_event

    @terminate_process_on_failure
    def run(self):
        with self._open():
            while True:
                can_read, _, _ = select([self._read_fd, self._stop_signal_rfd], [], [])
                if self._stop_signal_rfd in can_read:
                    self._stop_event.set()
                    break
                for msg in iter(self._read_fp.readline, b''):
                    self._msg_buf += msg
                    if self._msg_buf.endswith(b'\n'):
                        self._message_handler(self._msg_buf[:-1])
                        self._msg_buf = b''

    @contextmanager
    def _open(self):
        self._read_fd = open(self._pipe_path, O_RDONLY | O_NONBLOCK)
        self._read_fp = fdopen(self._read_fd, 'rb')
        self._prevent_eof_fd = open(self._pipe_path, O_WRONLY)
        yield
        self._read_fp.close()
        close(self._prevent_eof_fd)
        close(self._stop_signal_rfd)
        close(self._stop_signal_wfd)


    def stop(self):
        if self.is_alive():
            self._unblock()
        self.join()

    def _unblock(self):
        write(self._stop_signal_wfd, b'1')
