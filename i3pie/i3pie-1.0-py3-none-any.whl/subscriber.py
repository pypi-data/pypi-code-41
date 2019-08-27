import time
import queue
import socket
import threading

from .exceptions import IPCError


class SubscriberList:
    """List of Subscribers.

    Convenience wrapper to stop/notify/start/prune all subscribers at once.
    """
    def __init__(self):
        self._subscribers = []

    def __iter__(self):
        return iter(self._subscribers)

    def __getitem__(self, index):
        return self._subscribers[index]

    def __len__(self):
        return len(self._subscribers)

    def append(self, sub):
        self._subscribers.append(sub)

    def start(self):
        for sub in self._subscribers:
            sub.start()

    def stop(self):
        for sub in self._subscribers:
            if not sub.is_alive():
                continue
            while True:
                try:
                    # Consume all queued events
                    sub.event_queue.get_nowait()
                except queue.Empty:
                    break
            # Signal the thread to stop by sending `None` as data.
            sub.event_queue.put(None)
            sub.join()

    def notify(self, event_mask, data):
        for sub in self._subscribers:
            if sub.event_mask & event_mask:
                try:
                    sub.event_queue.put_nowait((event_mask, data))
                except queue.Full:
                    pass

    def prune(self):
        self._subscribers = [
            sub for sub in self._subscribers if sub.is_alive() and sub.subscribed
        ]


class Subscriber(threading.Thread):
    """Subscriber thread.

    Created for each subscription (Connection.subscribe() call).

    Started on Connection.listen() and left running indefinitely to listen for events.

    When ``IPCError`` or ``socket.error`` exceptions are raised during the execution of the
    ``run`` method, we retry to connect for at maximum ``conn.retry_window`` seconds and the
    give up and stop the thread. If any other ``Exception`` is raised, the thread stops
    immediately.

    Attributes:
        event_mask (consts.Flag): The event the subscriber is listening for.
        event_queue (queue.Queue): The queue of incoming events.
        _subscribed (threading.Event): Whether or not the subscriber is active. When the
            Event is cleared, the thread stops.
        _once (bool): Whether or not we should execute the callback once and then stop
            the thread.
        _callback (callable): The callback function to be executed on each event.
            Signature: _callback(Subscriber, Connection, consts.Event, dict)
        _conn_factory (callable): The function used to create a new ``Connection`` to be
            passed to the ``_callback`` function. It is a different ``Connection`` than the
            one used to create the ``Subscriber``.
        _conn (Connection): The current ``Connection``.
    """
    def __init__(self, event_mask, callback, event_queue, conn_factory, once=False):
        super().__init__()
        self.event_mask = event_mask
        self.event_queue = event_queue
        self._subscribed = threading.Event()
        self._subscribed.set()
        self._once = once
        self._callback = callback
        self._conn_factory = conn_factory
        self._conn = None

    @property
    def subscribed(self):
        return self._subscribed.is_set()

    def unsubscribe(self):
        self._subscribed.clear()

    def run(self):
        # The `time()` of the first of a series of errors
        err_time = None
        event = None
        try:
            while self.subscribed:
                try:
                    if self._conn is None:
                        self._conn = self._conn_factory()
                    while self.subscribed:
                        if event is None:
                            event = self.event_queue.get()
                        if event is None:
                            return
                        self._callback(self, self._conn, *event)
                        if self._once:
                            self.unsubscribe()
                        err_time = None
                        event = None
                except (IPCError, socket.error):
                    # Keep trying to connect when connection errors happens but for no
                    # more than `self._conn.retry_window` seconds.
                    if not self._conn:
                        break
                    self._conn.close()
                    now = time.time()
                    if err_time is None:
                        err_time = now
                    if now - err_time > self._conn.retry_window:
                        break
                    time.sleep(self._conn.retry_interval)
                    self._conn = None
                except Exception:
                    raise
        finally:
            self.unsubscribe()
            if self._conn:
                self._conn.close()
