from collections import deque
from threading import Lock, Condition


class Deque:
    def __init__(self):
        self._queue = deque()

        self._mutex = Lock()
        self._not_empty = Condition(self._mutex)

    def pop(self):
        with self._mutex:
            while not self._queue:
                self._not_empty.wait()
            return self._queue.pop()

    def push(self, item):
        self._push(item, self._queue.appendleft)

    def push_front(self, item):
        self._push(item, self._queue.append)

    def _push(self, item, put_method):
        with self._mutex:
            put_method(item)
            self._not_empty.notify()
