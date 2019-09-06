"""
Roax worker module.
"""

import threading


class PeriodicWorker(threading.Thread):

    def __init__(self, delay):
        self.delay = delay

    def start(self):
        pass

    def work(self):
        pass

    

class Workers:
