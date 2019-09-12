from threading import Thread


class CatchThread(Thread):
    def run(self):
        self.__trace = None
        try:
            self._target(*self._args, **self._kwargs)
        except:
            import sys
            self.__trace = sys.exc_info()

    def has_error(self):
        return self.__trace is not None

    def get_error_if_exists(self):
        if self.has_error():
            return {
                'name': self.getName(),
                'trace': self.__trace[2]
            }
