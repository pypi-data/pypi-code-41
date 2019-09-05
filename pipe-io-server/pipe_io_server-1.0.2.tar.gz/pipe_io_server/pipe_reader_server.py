from .pipe import Pipe, DEFAULT_PERMISSIONS
from .pipe_io_thread import PipeIOThread
from .pipe_reader_thread import PipeReaderThread


class PipeReaderServer(PipeIOThread):
    def __init__(
            self,
            in_pipe,
            permissions=DEFAULT_PERMISSIONS,
            manage_pipes=True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._reader_thread = None
        self._manage_pipes = manage_pipes
        self._in_pipe = in_pipe
        if self._manage_pipes:
            Pipe(self.in_pipe).recreate(permissions)

    @property
    def in_pipe(self):
        return self._in_pipe

    def _io_threads(self):
        self._reader_thread = PipeReaderThread(
            self.in_pipe,
            self._stop_event,
            self.handle_message
        )
        yield self._reader_thread

    def handle_message(self, message):
        raise NotImplementedError()

    def stop(self):
        super().stop()
        if self._manage_pipes:
            Pipe(self.in_pipe).remove()
