from .AtomicBase import *


class Base:
    def __init__(self, capacity, atomic_base):
        self.base = []
        self.base_str = []

        for ph in range(capacity+1):
            for at in atomic_base.base:
                # if ph + at[1] <= capacity:
                self.base.append([ph, at[0]])
                self.base_str.append(str([ph, at[0]]))

    def print(self):
        for i in self.base:
            print(i)
