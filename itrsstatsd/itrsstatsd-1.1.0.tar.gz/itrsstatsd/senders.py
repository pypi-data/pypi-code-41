# -*- coding: utf-8 -*-

import queue
import random
import threading

from .units import Unit

class StatsdMetricsSender:

    def __init__(self, channel, capacity=1024):
        self._channel = channel
        self._queue = queue.Queue(maxsize=capacity)
        self._stop_event = threading.Event()
        self._sender_thread = threading.Thread(target=self._process_queue, daemon=True).start()
        self._drop_count = 0

    def close(self):
        self._stop_event.set()
        self._channel.close()

    def on_counter(self, name, count, sample_rate: float, **dimension_kwargs):
        if not _should_send(sample_rate):
            return

        counter = "{0}:{1}|c".format(name, count)

        if 0.0 < sample_rate < 1.0:
            counter += "@{0}".format(sample_rate)

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

    def on_timer(self, name, millis, sample_rate : float, **dimension_kwargs):
        if not _should_send(sample_rate):
            return

        timer = "{0}:{1}|ms".format(name, millis)

        if 0.0 < sample_rate < 1.0:
            timer += "@{0}".format(sample_rate)

        self._enqueue(_append_dimensions(timer, **dimension_kwargs))

    def _enqueue(self, msg):
        try:
            self._queue.put_nowait(msg)
        except queue.Full:
            self._drop_count += 1
            pass

    def _process_queue(self):
        while not self._stop_event.is_set():
            msg = self._queue.get()
            self._channel.send(msg)

    def _get_drop_count(self):
        return self._drop_count


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
