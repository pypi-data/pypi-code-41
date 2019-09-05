from .pipe import Pipe, DEFAULT_PERMISSIONS
from .pipe_io_thread import PipeIOThread
from .pipe_writer_thread import PipeWriterThread


class PipeWriterServer(PipeIOThread):
    def __init__(
            self,
            out_pipe,
            permissions=DEFAULT_PERMISSIONS,
            manage_pipes=True,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._writer_thread = None
        self._manage_pipes = manage_pipes
        self._out_pipe = out_pipe
        if self._manage_pipes:
            Pipe(self.out_pipe).recreate(permissions)

    @property
    def out_pipe(self):
        return self._out_pipe

    def _io_threads(self):
        self._writer_thread = PipeWriterThread(
            self.out_pipe,
            self._stop_event
        )
        yield self._writer_thread

    def send_message(self, message):
        self._writer_thread.write(message)

    def stop(self):
        super().stop()
        if self._manage_pipes:
            Pipe(self.out_pipe).remove()
