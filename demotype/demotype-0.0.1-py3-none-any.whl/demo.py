
from pynput.keyboard import Key, Controller
import time
from random import random

class Doc(object):

    def __init__(self, text, delay=0.05, start_delay=0.5, fuzz_delay=0.15):
        self.kb = Controller()
        self.lines = text.split("\n")
        self.cur = 0
        self.delay = delay
        self.start_delay = start_delay
        self.fuzz_delay = fuzz_delay

    def print_next(self):
        if self.cur >= len(self.lines):
            return False
        time.sleep(self.start_delay)
        for c in self.lines[self.cur]:
            time.sleep(self.delay + self.fuzz_delay * random())
            self.kb.type(c)
        self.cur += 1
        return True

