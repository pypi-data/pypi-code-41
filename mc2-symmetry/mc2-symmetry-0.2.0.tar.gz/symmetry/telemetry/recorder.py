import os
import threading
from abc import ABC


class TelemetryRecorder(ABC, threading.Thread):

    def __init__(self, rds, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rds = rds
        self._sub = None
        self.thread = None

    def stop(self):
        self.close()

        if self.thread:
            self.thread.join()

    def close(self):
        if self._sub:
            self._sub.close()

    def run(self):
        self._sub = TelemetrySubscriber(self.rds)
        sub = self._sub.run()

        for timestamp, metric, node, value in sub:
            self._record(timestamp, metric, node, value)

    def _record(self, timestamp, metric, node, value):
        raise NotImplementedError()


class TelemetryPrinter(TelemetryRecorder):

    def _record(self, timestamp, metric, node, value):
        print(timestamp, metric, node, value)


class TelemetryFileRecorder(TelemetryRecorder):
    """
       Records the output of a telemetry subscriber.

       :param rds: redis client
       :param fpath: the file to write to
       :param flush_every: the number of records to buffer before flushing
       """

    def __init__(self, rds, fpath, flush_every=36) -> None:
        super().__init__(rds)
        self.fpath = fpath
        self.flush_every = flush_every
        self.fd = None
        self.i = 0

    def run(self):
        with open(self.fpath, 'w') as fd:
            try:
                self.fd = fd
                super().run()
            finally:
                self.fd.flush()

    def _record(self, timestamp, metric, node, value):
        self.i = (self.i + 1) % self.flush_every
        self.fd.write(','.join([timestamp, metric, node, value]) + os.linesep)
        if self.i == 0:
            self.fd.flush()


class TelemetryRedisRecorder(TelemetryRecorder):
    """
    Writes telemetry data from a subscription back into redis and garbage collects old data.
    """

    key_prefix = 'telemc:'

    def __init__(self, rds) -> None:
        super().__init__(rds)

    def _record(self, timestamp, metric, node, value):
        rds = self.rds

        key = '%s%s:%s' % (self.key_prefix, node, metric)
        score = float(timestamp)
        val = '%s %s' % (timestamp, value)

        rds.zadd(key, {val: score})


class TelemetryDashboardRecorder(TelemetryRecorder):
    """
    Writes telemetry data from a subscription back into redis and garbage collects old data.
    """

    def _record(self, timestamp, metric, node, value):
        rds = self.rds

        key = 'metrics:%s:%s' % (node, metric)
        score = float(timestamp)
        val = '%s %s' % (timestamp, value)

        rds.zadd(key, {val: score})
        rds.zremrangebyscore(key, 0, score - 69)  # garbage collect (for some reason 69 keeps 60 seconds ...)


class TelemetrySubscriber:

    def __init__(self, rds, pattern='telemetry:*') -> None:
        super().__init__()
        self.rds = rds
        self.pattern = pattern
        self.pubsub = None

    def run(self):
        self.pubsub = self.rds.pubsub()

        try:
            self.pubsub.psubscribe(self.pattern)

            for item in self.pubsub.listen():
                data = item['data']
                if type(data) == int:
                    continue
                channel = item['channel']
                timestamp, value = data.split(' ')
                _, metric, node = channel.split(':')

                yield (timestamp, metric, node, value)
        finally:
            self.pubsub.close()

    def close(self):
        if self.pubsub:
            self.pubsub.punsubscribe()
