from .pipe import DEFAULT_PERMISSIONS
from .pipe_reader_server import PipeReaderServer
from .pipe_writer_server import PipeWriterServer


class PipeIOServer(PipeReaderServer, PipeWriterServer):
    # pylint: disable=abstract-method
    def __init__(
            self,
            in_pipe,
            out_pipe,
            permissions=DEFAULT_PERMISSIONS,
            manage_pipes=True
    ):
        super().__init__(
            in_pipe=in_pipe,
            out_pipe=out_pipe,
            permissions=permissions,
            manage_pipes=manage_pipes
        )

    def _io_threads(self):
        # pylint: disable=no-member
        yield from PipeReaderServer._io_threads(self)
        yield from PipeWriterServer._io_threads(self)
