import atexit
import logging
import threading
import time
from abc import abstractmethod

from scopeagent.recorders.utils import fix_timestamps

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty

from ..tracer import tags, SpanRecorder


LOOP_PERIOD = 1  # seconds between buffer checks
logger = logging.getLogger(__name__)


class AsyncRecorder(SpanRecorder):
    def __init__(self, period=1, test_only=True):
        super(AsyncRecorder, self).__init__()
        self.period = period
        self._queue = Queue()
        self._thread = None
        self.test_only = test_only
        self.ensure_running_thread()

    def ensure_running_thread(self):
        if not self._thread:
            logger.debug("starting asyncrecorder thread")
            self._thread = threading.Thread(target=self.run)
            self._thread.daemon = True
            self._thread.start()
            atexit.register(self.stop)

    def record_span(self, span):
        if not span.context.sampled:
            return

        if self.test_only and span.context.baggage.get(tags.TRACE_KIND) != 'test':
            return

        self._queue.put(fix_timestamps(span), block=False)
        self.ensure_running_thread()

    def run(self):
        running = True
        buffer = []
        loop_duration = 0
        while running:
            time.sleep(LOOP_PERIOD)
            loop_duration += LOOP_PERIOD
            try:
                while True:
                    item = self._queue.get(block=False)
                    self._queue.task_done()
                    if item is None:
                        running = False
                        raise Empty()
                    buffer.append(item)
            except Empty:
                pass

            # We flush the buffer if any of the following apply:
            # * Last time we flushed was more than `self.period` seconds ago (even if buffer is empty)
            # * The recorder is being shut down
            # * There is data to be flushed in the buffer
            if loop_duration >= self.period or not running or len(buffer) > 0:
                loop_duration = 0
                try:
                    self.flush(buffer)
                    buffer = []
                except Exception as e:
                    logger.debug("exception while flushing buffer - trying again in next iteration: %s", str(e))

    def stop(self):
        try:
            if self._thread:
                logger.debug("stopping asyncrecorder thread")
                self._queue.put(None)
                self._thread.join()
        except Exception as e:
            logger.debug("failed to stop: %s", e)

    @abstractmethod
    def flush(self, spans):
        raise NotImplementedError()
