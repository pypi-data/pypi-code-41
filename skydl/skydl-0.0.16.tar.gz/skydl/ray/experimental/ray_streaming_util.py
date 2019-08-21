# -*- coding: utf-8 -*-
from ray.experimental.streaming.communication import QueueConfig


class DefaultStreamingEnvConfig(object):
    """
    default ray streaming env config
    """
    def __init__(self, max_size=999999,
                max_batch_size=99999,
                max_batch_time=0.01,
                prefetch_depth=10,
                background_flush=False,
                parallelism=1):
        self.queue_config = QueueConfig(
            max_size=max_size,
            max_batch_size=max_batch_size,
            max_batch_time=max_batch_time,
            prefetch_depth=prefetch_depth,
            background_flush=background_flush)
        self.parallelism = parallelism


class DefaultStreamingSource(object):
    """default streaming source implement"""
    def get_next(self):
        # get current record
        return None


class StreamingRecord(object):
    """
    A class used to streaming transformer
    @:param tuple_value e.g. ("00700.HK", [open, high, low, close]) or ("ok",1), ("fail",0)
    """
    def __init__(self, tuple_value):
        k, v = tuple_value
        self.key = k
        self.record = tuple_value

    def get_value(self):
        if self.record is None:
            return None
        return self.record[1]


