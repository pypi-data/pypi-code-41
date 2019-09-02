"""
    A broadacasting dictionary that waits a loop for changes
"""
import time
from bluemax.utils import json_utils


class Status:
    """
        Simple helper class of dictionary
        that calls you every time it changes
    """

    def __init__(self, ioloop, callback, values=None, timeout=0.1):
        self.ioloop = ioloop
        self._items_ = values if values is not None else {}
        self._last_ = None
        self._callback_ = callback
        self._timeout_ = timeout
        self._pending_ = None

    def __getitem__(self, key):
        """ have an item """
        return self._items_.get(key)

    def __setitem__(self, key, value):
        """ change and flag we need to test for change """
        self._items_[key] = value
        if self._pending_ is not None:
            self.ioloop.remove_timeout(self._pending_)
        self._pending_ = self.ioloop.add_timeout(
            time.time() + self._timeout_, self._do_callback_
        )

    def _do_callback_(self):
        """ if we've change call our callback """
        self._pending_ = None
        now = json_utils.dumps(self)
        if self._last_ != now:
            self._last_ = now
            self._callback_(self)

    @property
    def items(self):
        """ return the data we're holding """
        return self._items_

    def to_json(self):
        """ We work well with json_utils """
        return self._items_

    def __repr__(self):
        """ we print nicely """
        return repr(self._items_)
