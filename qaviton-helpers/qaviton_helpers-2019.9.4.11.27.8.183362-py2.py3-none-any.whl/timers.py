from time import time, sleep


class DynamicWait:
    """ sleep dynamically by measuring the time passed
    since t started and sleeping the
    remaining of the delay
    """

    def __init__(self, duration):
        self.t = time()
        self.d = duration

    def __call__(self):
        t = time() - self.t
        if t < self.d:
            sleep(self.d - t)
