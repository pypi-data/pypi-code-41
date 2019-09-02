import numpy as np


class State:
    def __init__(self, capacity, n):
        self.capacity = capacity
        self.n = n
        self.dims = [self.capacity+1] + [2]*self.n

        self.state_list = [0] + [0]*self.n

    def state(self):
        return [self.state_list[0], self.state_list[1:]]

    def inc(self):
        for i in range(len(self.state_list)-1, -1, -1):
            if self.state_list[i] < self.dims[i]-1:
                # if self.state_list[i] < self.dims[i]-1 and np.sum(self.state_list) < self.capacity:
                self.state_list[i] += 1

                return True
            else:
                self.state_list[i] = 0

        return False
