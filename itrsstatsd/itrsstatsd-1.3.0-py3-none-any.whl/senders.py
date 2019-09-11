# -*- coding: utf-8 -*-
#
# Copyright 2019 ITRS Group Ltd. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import random
import sys
import threading

from .units import Unit


class StatsdMetricsSender:

    def __init__(self, channel, capacity=1024):
        self._channel = channel
        self._queue = CircularQueue(capacity=capacity)
        self._stop_event = threading.Event()
        self._sender_thread = threading.Thread(target=self._process_queue, daemon=True).start()
        self._warned_drop = False

    def close(self):
        self._stop_event.set()
        self._channel.close()

    def on_counter(self, name, count, sample_rate: float, **dimension_kwargs):
        if not _should_send(sample_rate):
            return

        counter = "{0}:{1}|c".format(name, count)

        if 0.0 < sample_rate < 1.0:
            counter += "|@{0}".format(sample_rate)

        self._enqueue(_append_dimensions(counter, **dimension_kwargs))

    def on_gauge(self, name, value: float, is_delta: bool, unit: Unit, **dimension_kwargs):
        gauge = "{0}:".format(name)

        if is_delta and value > 0.0:
            gauge += "+"

        gauge += "{0}|g".format(value)

        if unit is not None and unit is not Unit.Empty:
            gauge += "|u:{0}".format(unit.get_description())

        self._enqueue(_append_dimensions(gauge, **dimension_kwargs))

    def on_set(self, name, identifier, **dimension_kwargs):
        gauge = "{0}:{1}|s".format(name, identifier)
        self._enqueue(_append_dimensions(gauge, **dimension_kwargs))

    def on_timer(self, name, elapsed, sample_rate : float, **dimension_kwargs):
        if not _should_send(sample_rate):
            return

        timer = "{0}:{1}|ms".format(name, elapsed)

        if 0.0 < sample_rate < 1.0:
            timer += "|@{0}".format(sample_rate)

        self._enqueue(_append_dimensions(timer, **dimension_kwargs))

    def _enqueue(self, msg):
        if self._queue.add(msg) > 0 and not self._warned_drop:
            self._warned_drop = True
            print("At least one statsd message was dropped due to a full sending queue. " +
                  "This may indicate a network problem or that a larger sending queue size " +
                  "is necessary to support the load. This error will not be logged again.",
                  file=sys.stderr)

    def _process_queue(self):
        while not self._stop_event.is_set():
            msg = self._queue.poll(.1)
            if msg is not None:
                self._channel.send(msg)


def _should_send(sample_rate: float):
    if sample_rate <= 0.0:
        return False

    if sample_rate >= 1.0:
        return True

    return sample_rate > random.random()


def _append_dimensions(message, **dimension_kwargs):
    if dimension_kwargs is not None and len(dimension_kwargs) > 0:
        message += "|#"
        for key, value in dimension_kwargs.items():
            message += "{0}:{1},".format(key, value)
        message = message[0:-1]

    return message


class CircularQueue:

    def __init__(self, capacity=1024):
        self._elements = [None] * capacity
        self._start = 0
        self._end = 0
        self._capacity = capacity
        self._full = False
        self._lock = threading.RLock()
        self._not_empty = threading.Condition(self._lock)
        self._dropped = 0

    def add(self, msg):
        """Returns total number of messages dropped"""

        with self._lock:
            if self._full:
                self._increment_start()
                self._dropped += 1

            self._elements[self._end] = msg
            self._increment_end()

            if self._end == self._start:
                self._full = True

            self._not_empty.notify()
        return self._dropped

    def _increment_start(self):
        self._start += 1
        if self._start == self._capacity:
            self._start = 0

    def _increment_end(self):
        self._end += 1
        if self._end == self._capacity:
            self._end = 0

    def poll(self, timeout):
        msg = None
        with self._lock:
            if self._size() > 0 or self._not_empty.wait(timeout):
                msg = self._elements[self._start]
                self._elements[self._start] = None
                self._increment_start()
                self._full = False
        return msg

    def _size(self):
        if self._start == self._end:
            return self._capacity if self._full else 0
        if self._end < self._start:
            return self._capacity - self._start + self._end
        return self._end - self._start

    def size(self):
        with self._lock:
            return self._size()
