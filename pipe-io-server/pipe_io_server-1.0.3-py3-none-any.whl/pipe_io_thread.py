from threading import Thread, Event

from .terminate_process_on_failure import terminate_process_on_failure


class PipeIOThread(Thread):
    def __init__(self, **kwargs):
        super().__init__(daemon=True)
        self._stop_event = Event()
        self.__io_threads = []

    def start(self):
        super().start()
        self.__io_threads.extend(self._io_threads())
        for thread in self.__io_threads:
            thread.start()

    @terminate_process_on_failure
    def run(self):
        self._stop_event.wait()
        self._stop_threads()

    def _io_threads(self):
        raise NotImplementedError()

    def _stop_threads(self):
        for thread in self.__io_threads:
            if thread.is_alive():
                thread.stop()
        self.on_stop()

    def on_stop(self):
        pass

    def stop(self):
        self._stop_event.set()
        if self.is_alive():
            self.join()

    def wait(self):
        self._stop_event.wait()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type_, value, tb):
        self.stop()
