from contextlib import contextmanager
from signal import signal
import _thread
import threading


class TimeoutError(RuntimeError):
    """An error raised whenever timeout is reached."""
    pass


@contextmanager
def timeout(seconds, exception_cls=TimeoutError):
    if hasattr(signal, "SIGALRM"):
        def _signal_handler(signum, frame):
            raise exception_cls("Timeout after {seconds} seconds.")
        signal.signal(signal.SIGALRM, _signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
        timer.start()
        try:
            yield
        except KeyboardInterrupt:
            raise exception_cls(f"Timeout after {seconds} seconds.")
        finally:
            timer.cancel()