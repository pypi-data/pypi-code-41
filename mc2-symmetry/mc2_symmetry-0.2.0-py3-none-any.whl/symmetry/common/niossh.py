import abc
import logging
import os
import selectors
import threading
import traceback
from typing import List, Callable

import paramiko

logger = logging.getLogger(__name__)


class ChannelHandler:
    BUF_SIZE = 4096

    def __init__(self) -> None:
        super().__init__()
        self.stdout: List[bytearray] = None
        self.stderr: List[bytearray] = None

    def read(self, channel):
        buf = channel.recv(self.BUF_SIZE)

        if buf.endswith(b'\n'):
            if self.stdout:
                self.stdout.append(buf)
                buf = b''.join(self.stdout)
                self.stdout.clear()

            for line in buf.splitlines():
                self.on_line(channel, str(line, 'UTF-8'))

        else:
            if self.stdout is None:
                self.stdout = list()

            self.stdout.append(buf)

    def read_stderr(self, channel):
        buf = channel.recv_stderr(self.BUF_SIZE)

        if buf.endswith(b'\n'):
            if self.stderr:
                self.stderr.append(buf)
                buf = b''.join(self.stderr)
                self.stderr.clear()

            for line in buf.splitlines():
                self.on_line_stderr(channel, str(line, 'UTF-8'))

        else:
            if self.stderr is None:
                self.stderr = list()

            self.stderr.append(buf)

    def on_line(self, channel, line: str):
        pass

    def on_line_stderr(self, channel, line: str):
        pass

    def on_eof(self, channel):
        pass

    def on_transport_closed(self, channel):
        pass


class PrintingChannelHandler(ChannelHandler):

    def on_line(self, channel, line: str):
        print('on_line')
        print('  - channel:', channel)
        print('  - line   :', line)

    def on_line_stderr(self, channel, line: str):
        print('on_line_stderr')
        print('  - channel:', channel)
        print('  - line   :', line)

    def on_eof(self, channel):
        print('on_eof')
        print('  - channel:', channel)


class Result:

    def __init__(self) -> None:
        super().__init__()
        self.stdout = list()
        self.stderr = list()
        self.channel = None

    @property
    def result(self):
        out = None
        err = None

        if self.stdout:
            out = os.linesep.join([line.strip() for line in self.stdout])
        if self.stderr:
            err = os.linesep.join([line.strip() for line in self.stderr])

        if err and out:
            return out + os.linesep + err
        elif out:
            return out
        elif err:
            return err
        else:
            return None

    def __str__(self) -> str:
        return 'Result(channel=%s, result=%s)' % (self.channel, self.result)


ResultHandler = Callable[[Result], None]


class ResultCollector(ChannelHandler):

    def __init__(self, handler: ResultHandler, aggregate=True) -> None:
        super().__init__()
        self.handler: ResultHandler = handler
        self.aggregate = Result() if aggregate else None

    def _result(self):
        return self.aggregate if self.aggregate is not None else Result()

    def on_result(self, channel, result: Result):
        result.channel = channel
        self.handler(result)

    def on_line(self, channel, line: str):
        result = self._result()
        result.stdout.append(line)

        if not self.aggregate:
            self.on_result(channel, result)

    def on_line_stderr(self, channel, line: str):
        result = self._result()
        result.stderr.append(line)

        if not self.aggregate:
            self.on_result(channel, result)

    def on_eof(self, channel):
        if self.aggregate:
            self.on_result(channel, self._result())


class CommandCallback(abc.ABC):
    def on_result(self, result: Result):
        raise NotImplementedError

    def on_exception(self, channel, exception):
        pass


class ResultPrinter(CommandCallback):
    def on_result(self, result):
        print('[%s]' % threading.current_thread().name, result)

    def on_exception(self, channel, exception):
        print('[%s]' % threading.current_thread().name, 'exception', channel, exception)
        traceback.print_exc()


class ChannelEventLoop:

    def __init__(self) -> None:
        super().__init__()
        self.selector: selectors.DefaultSelector = selectors.DefaultSelector()
        self._closed = False

    def register(self, channel, handler: ChannelHandler):
        channel.setblocking(False)
        # TODO: ValueError: I/O operation on closed epoll object
        self.selector.register(channel, selectors.EVENT_READ, data=handler)

    def unregister(self, channel):
        self.selector.unregister(channel)

    def exec_command(self, channel: paramiko.Channel, command: str, callback: CommandCallback, listen=False):
        logger.debug('executing command %s on channel %s', command, channel)
        channel.setblocking(False)
        try:
            channel.exec_command(command)
            self.register(channel, ResultCollector(callback.on_result, not listen))
        except Exception as e:
            self.unregister(channel)
            callback.on_exception(channel, e)

    def run(self):
        selector = self.selector

        while not self._closed:
            for key, event in selector.select(5):
                # TODO: POISON channel instead of timeout
                #  https://stackoverflow.com/questions/4660756/interrupting-select-to-add-another-socket-to-watch-in-python
                channel: paramiko.Channel = key.fileobj
                handler: ChannelHandler = key.data

                if channel.recv_ready():
                    handler.read(channel)
                elif channel.recv_stderr_ready():
                    handler.read_stderr(channel)
                else:
                    selector.unregister(channel)
                    handler.on_eof(channel)
                    if not channel.transport.is_active():
                        handler.on_transport_closed(channel)
                    continue

                if channel.eof_received:
                    # checking here can skip a selection iteration for the channel
                    selector.unregister(channel)
                    handler.on_eof(channel)
                    if not channel.transport.is_active():
                        handler.on_transport_closed(channel)

    def is_closed(self):
        return self._closed

    def close(self):
        self._closed = True
        self.selector.close()
