class State:
    def __init__(self, capacity, n_atoms, n_levels):
        self.capacity = capacity
        self.n_atoms = n_atoms
        self.n_levels = n_levels

        self.stop = False

        self.state = [0, [0] * self.n_atoms]

    def inc_at(self):
        for n_ in range(self.n_atoms - 1, -1, -1):
            if self.state[1][n_] == self.n_levels-1:
                self.state[1][n_] = 0

                continue

            self.state[1][n_] += 1

            return True

        return False

    def inc(self):
        if self.stop:
            return False

        # print("stop:", self.stop)

        if self.inc_at():
            return True

        return self.inc_ph()

    def inc_ph(self):
        # print(self.state[0])

        if self.state[0] == self.capacity:
            self.stop = True
            # exit(0)
            return False

        if self.state[0] < self.capacity:
            self.state[0] += 1

            # self.clear_at()
            # print(self.state)

            return True

        return False

    def clear_at(self):
        for n_ in range(self.n_atoms):
            self.state[1][n_] = 0
# import numpy as np


# class State:
#     def __init__(self, capacity, n):
#         self.capacity = capacity
#         self.n = n
#         self.dims = [self.capacity+1] + [2]*self.n

#         self.state_list = [0] + [0]*self.n

#     def state(self):
#         return [self.state_list[0], self.state_list[1:]]

#     def inc(self):
#         for i in range(len(self.state_list)-1, -1, -1):
#             if self.state_list[i] < self.dims[i]-1:
#                 # if self.state_list[i] < self.dims[i]-1 and np.sum(self.state_list) < self.capacity:
#                 self.state_list[i] += 1

#                 return True
#             else:
#                 self.state_list[i] = 0

#         return False
