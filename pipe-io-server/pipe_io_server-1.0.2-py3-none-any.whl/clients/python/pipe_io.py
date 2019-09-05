from typing import Callable


class PipeReader:
    def __init__(self, pipe_path):
        self._pipe = open(pipe_path, 'rb')
        self._message_handler = lambda msg: None

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def close(self):
        self._pipe.close()

    @property
    def message_handler(self):
        return self._message_handler

    @message_handler.setter
    def message_handler(self, value):
        if not isinstance(value, Callable):
            raise ValueError("message_handler must be callable!")
        self._message_handler = value

    def run(self):
        msg = self.recv_message()
        while msg:
            self._message_handler(msg)
            msg = self.recv_message()

    def recv_message(self):
        return self._pipe.readline()[:-1]


class PipeWriter:
    def __init__(self, pipe_path):
        self._pipe = open(pipe_path, 'wb')

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def close(self):
        self._pipe.close()

    def send_message(self, message):
        self._pipe.write(message + b'\n')
        self._pipe.flush()


class PipeIO:
    def __init__(self, in_pipe_path, out_pipe_path):
        self.reader = PipeReader(in_pipe_path)
        self.writer = PipeWriter(out_pipe_path)

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def close(self):
        self.reader.close()
        self.writer.close()
