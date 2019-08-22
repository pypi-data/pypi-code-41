import threading


class InfinityThread(threading.Thread):
    def __init__(self, interval, target, args=None, kwargs=None, on_stop_func=None, on_stop_args=None,
                 on_stop_kwargs=None,
                 ignore_errors=False):
        """
        :param interval: time in seconds between `target` function calls.
        :param target: is the callable object to be invoked when the thread starts.
        :param args: is the argument tuple for the `target` invocation. Defaults to ().
        :param kwargs: is a dictionary of keyword arguments for the `target` invocation. Defaults to {}
        :param on_stop_func: is the callable object to be invoked when the thread stops.
        :param on_stop_args: is the argument tuple for the `on_stop_func` invocation. Defaults to ().
        :param on_stop_kwargs: is a dictionary of keyword arguments for the `on_stop_func` invocation. Defaults to {}
        :param ignore_errors: If set to `True` the thread will keep running even after failure in `target` function.
        """
        super().__init__()
        self._stop_event = threading.Event()

        self._interval = interval
        self._target = target
        self._args = args if args is not None else ()
        self._kwargs = kwargs if kwargs is not None else {}
        self._on_stop = on_stop_func
        self._on_stop_args = on_stop_args if on_stop_args is not None else ()
        self._on_stop_kwargs = on_stop_kwargs if on_stop_kwargs is not None else {}
        self._ignore_errors = ignore_errors

    def run(self):
        while not self.stopped:
            try:
                self._target(*self._args, **self._kwargs)
            except Exception:
                if not self._ignore_errors:
                    raise
            self._sleep(self._interval)

    @property
    def stopped(self):
        return self._stop_event.is_set()

    def _sleep(self, seconds):
        self._stop_event.wait(seconds)

    def stop(self):
        self._stop_event.set()
        if self._on_stop:
            self._on_stop(*self._on_stop_args, **self._on_stop_kwargs)
