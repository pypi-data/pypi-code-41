# -*- coding: utf-8 -*-
"""Print module.

contains Printer
"""

from multiprocessing import Queue
from time import time


class Printer:
    """Printer class.

    This class is the basis for a file-like object which sends all text written
    to it through a multiprocessing queue. The input is accumulated and only
    passed through the queue every 10 ms (default value, may be set on init).
    This leads to a huge speedup for a large number of small inputs.
    """

    def __init__(self, queue: Queue, sendEvery: float = 0.01):
        """Initialise file-like object.

        Args:
            queue (Queue): Multiprocessing queue to be used.
            sendEvery (float): Minimum temporal distance between two sends.
                In seconds. The input is accumulated during this time. Default
                value is 10 ms.
        """
        self.__curStdout, self.__lastOutSendTime = "", time()
        self.__queue = queue
        self.__sendEvery = sendEvery

    @property
    def currentStdOut(self) -> str:
        """Current cached content written to this file-like object (str)."""
        return self.__curStdout

    def write(self, text: str):
        """Write..."""
        self.__curStdout += text

        if time() > self.__lastOutSendTime + self.__sendEvery:
            self.__queue.put(self.__curStdout)
            self.__curStdout, self.__lastOutSendTime = "", time()
