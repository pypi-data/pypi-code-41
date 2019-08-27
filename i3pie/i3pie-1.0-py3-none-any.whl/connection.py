import json
import os
import queue
import select
import socket
import struct
import subprocess
import time
from itertools import chain
from collections.abc import Iterable

from .consts import MessageType, EventType, Event
from .subscriber import Subscriber, SubscriberList
from .exceptions import IPCError, EmptySubscriberList

from .models import (
    Container,
    WorkspaceReply,
    OutputReply,
    CommandReply,
    VersionReply,
    MarksReply,
    BindingModesReply,
    ConfigReply,
    BarConfigReply,
    BarsListReply,
    SubscribeReply,
    TickReply,
    SyncReply,
)


class Connection:
    """Connection to i3wm

    Attributes:
        socket_path (str): the socket file path used by i3. Defaults to the ``I3SOCK``
            environment variable or the value returned by ``i3 --get-socketpath``, in this
            order.
        retry_window (int): The maximum time in seconds we should retry to connect in
            case of a connection error.
        retry_interval (float): Step in seconds of every retry.
        event_queue_size (int): The event queue max size. When the queue is full events
            are dropped.
        event_socket_timeout (int) The event socket timeout in seconds.
    """
    _MAGIC = b"i3-ipc"
    _HEADER_STRUCT = struct.Struct(f"={len(_MAGIC)}sII")
    _BUF_SIZE = 4096

    def __init__(self, socket_path=None):

        if not socket_path:
            socket_path = os.environ.get("I3SOCK")
        if not socket_path:
            socket_path = self._get_socket_path()
        if not socket_path:
            raise RuntimeError("unable to retrieve i3 socket path")

        self.socket_path = socket_path

        self.retry_window = 3
        self.retry_interval = 0.1
        self.event_queue_size = 30
        self.event_socket_timeout = 1

        self._subscribers = SubscriberList()

        try:
            self._socket = self._new_socket()
            self._event_socket = self._new_socket()
        except socket.error:
            raise

    def _new_connection(self):
        conn = Connection(socket_path=self.socket_path)
        conn.retry_window = self.retry_window
        conn.retry_interval = self.retry_interval
        return conn

    def _new_socket(self):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
        except (FileNotFoundError, ConnectionRefusedError) as err:
            raise IPCError(f"socket file not found: {self.socket_path}") from err
        return sock

    def _get_socket_path(self):
        try:
            proc = subprocess.run(
                ("i3", "--get-socketpath"),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                encoding="utf8",
                check=True,
            )
            return proc.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def _close(self):
        self._socket.close()
        if self._event_socket:
            self._event_socket.close()

    def close(self):
        self._close()

    def command(self, command, *args):
        if args:
            # When a list of `Container`s is given, execute the command for each
            # `Container`.
            command_ = ""
            for con in chain(*(a if isinstance(a, Iterable) else (a,) for a in args)):
                command_ += f'[con_id="{con.id}"] {command};'
            command = command_

        reply = self._send_message(self._socket, MessageType.RUN_COMMAND, command)
        return CommandReply(reply)

    def get_tree(self):
        reply = self._send_message(self._socket, MessageType.GET_TREE)
        return self._build_tree(Container(self, reply, parent=None))

    def _build_tree(self, node):
        for attr in ("nodes", "floating_nodes"):
            setattr(
                node,
                attr,
                [
                    self._build_tree(Container(self, n, parent=node))
                    for n in getattr(node, attr)
                ],
            )
        return node

    def get_workspaces(self):
        for w in self._send_message(self._socket, MessageType.GET_WORKSPACES):
            yield WorkspaceReply(w)

    def get_outputs(self):
        for o in self._send_message(self._socket, MessageType.GET_OUTPUTS):
            yield OutputReply(o)

    def get_marks(self):
        reply = self._send_message(self._socket, MessageType.GET_MARKS)
        return MarksReply(reply)

    def get_binding_modes(self):
        reply = self._send_message(self._socket, MessageType.GET_BINDING_MODES)
        return BindingModesReply(reply)

    def get_version(self):
        reply = self._send_message(self._socket, MessageType.GET_VERSION)
        return VersionReply(reply)

    def get_config(self):
        reply = self._send_message(self._socket, MessageType.GET_CONFIG)
        return ConfigReply(reply)

    def get_bar_config(self, id=""):
        reply = self._send_message(self._socket, MessageType.GET_BAR_CONFIG, str(id))
        if isinstance(reply, list):
            return BarsListReply(reply)
        if not reply.get("id"):
            return None
        return BarConfigReply(reply)

    def send_tick(self, message):
        reply = self._send_message(self._socket, MessageType.SEND_TICK, message)
        return TickReply(reply)

    def sync(self, value):
        reply = self._send_message(self._socket, MessageType.SYNC, value)
        return SyncReply(reply)

    def subscribe(self, event_mask, callback, once=False):
        if not isinstance(event_mask, Event):
            raise ValueError(f"invalid event mask: {event_mask}")

        reply = SubscribeReply(self._subscribe(event_mask))
        if reply.success:
            event_queue = queue.Queue(self.event_queue_size)
            sub = Subscriber(
                event_mask,
                callback,
                event_queue,
                once=once,
                conn_factory=self._new_connection,
            )
            self._subscribers.append(sub)
            return True

        return False

    def _subscribe(self, event_mask):
        events = event_mask.canonical_names()
        payload = json.dumps(events)
        return self._send_message(self._event_socket, MessageType.SUBSCRIBE, payload)

    def listen(self):
        """Start listening for events and dispatch them to all subscribers.
        """
        if not self._subscribers:
            raise EmptySubscriberList("no registered subscribers")
        self._subscribers.start()
        try:
            self._event_loop()
        except EmptySubscriberList as err:
            return err
        except Exception:
            raise
        finally:
            self._subscribers.stop()
            self._close()

    def _event_loop(self):
        # The `time()` of the first of a series of errors.
        err_time = None
        while True:
            try:
                # Remove dead or inactive subscribers from the subscribers list.
                # Raise exception if after pruning there are no more active subscribers.
                self._subscribers.prune()
                if not self._subscribers:
                    raise EmptySubscriberList("no more subscribes")

                if self._event_socket is None:
                    # Create a new socket and resubscribe to all events if
                    # `self._event_socket` has been unset after a connection error.
                    self._event_socket = self._new_socket()
                    for sub in self._subscribers:
                        self._subscribe(sub.event_mask)

                readable, _, _ = select.select(
                    [self._event_socket], [], [], self.event_socket_timeout
                )
                if readable:
                    message_type, data = self._receive_message(self._event_socket)
                else:
                    # We use a timeout in order to periodically check if there are no
                    # more subscribers, and in that case, exit the program.
                    # This avoids having to wait undefinitely up until another even
                    # comes by in case we don't catch an inactive thread with
                    # `_subscribers.prune()`.
                    continue

                err_time = None

            except (IPCError, socket.error):
                # Keep trying to connect when connection errors happens but for no
                # more than `self.retry_window` seconds.
                now = time.time()
                if err_time is None:
                    err_time = now
                if now - err_time > self.retry_window:
                    raise

                time.sleep(self.retry_interval)

                if self._event_socket:
                    self._event_socket.close()
                self._event_socket = None

            else:
                # Check if the type is an event.
                # See https://i3wm.org/docs/ipc.html#_events
                if message_type >> 31 != 1:
                    continue

                event_mask = EventType(message_type & 0x7F).flag

                if event_mask & Event.WORKSPACE:
                    if data["current"]:
                        data["current"] = self._build_tree(
                            Container(self, data["current"], parent=None)
                        )
                    if data["old"]:
                        data["old"] = self._build_tree(
                            Container(self, data["old"], parent=None)
                        )
                if event_mask & Event.WINDOW:
                    if data["container"]:
                        data["container"] = self._build_tree(
                            Container(self, data["container"], parent=None)
                        )

                self._subscribers.notify(event_mask, data)

    def _send_message(self, sock, message_type, payload=""):
        _, data = self._send(sock, message_type, payload)
        return json.loads(data)

    def _receive_message(self, sock):
        message_type, data = self._recv(sock)
        return message_type, json.loads(data)

    def _send(self, sock, message_type, payload):
        payload = payload.encode("utf-8")
        header = self._HEADER_STRUCT.pack(self._MAGIC, len(payload), message_type.value)
        sock.sendall(header + payload)
        return self._recv(sock)

    def _recv(self, sock):
        header = self._recvall(sock, self._HEADER_STRUCT.size)
        magic, length, message_type = self._HEADER_STRUCT.unpack(header)
        return message_type, self._recvall(sock, length)

    def _recvall(self, sock, expected):
        data = b""
        while len(data) < expected:
            chunk = sock.recv(min(expected - len(data), self._BUF_SIZE))
            if not chunk:
                raise IPCError(f"socket connection closed")
            data += chunk
        return data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def __str__(self):
        return f"<Connection socket_path={self.socket_path!r}>"

    def __repr__(self):
        return f"Connection(socket_path={self.socket_path!r})"
