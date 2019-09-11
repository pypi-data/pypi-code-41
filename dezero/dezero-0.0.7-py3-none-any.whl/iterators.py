import math
import random
import numpy as np


class SerialIterator:

    def __init__(self, dataset, batch_size, repeat=True, shuffle=True):
        self.dataset = dataset
        self.batch_size = batch_size
        self.repeat = repeat
        self.shuffle = shuffle
        self.data_size = len(dataset)
        self.max_iter_per_epoch = math.ceil(self.data_size / batch_size)

        self.reset()

    def reset(self):
        self.epoch = 0
        self.is_new_epoch = False
        self.iteration = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.repeat and self.iteration >= self.max_iter_per_epoch:
            raise StopIteration

        i = self.iteration % self.max_iter_per_epoch
        start_idx = i * self.batch_size
        end_idx = (i + 1) * self.batch_size
        batch = self.dataset[start_idx:end_idx]

        self.iteration += 1

        epoch = self.iteration // self.max_iter_per_epoch
        self.is_new_epoch = self.epoch < epoch
        self.epoch = epoch

        if self.shuffle and self.is_new_epoch:
            random.shuffle(self.dataset)

        return batch

    def next(self):
        return self.__next__()


class RnnIterator:

    def __init__(self, dataset, batch_size):
        self.xs = dataset[:-1]
        self.ts = dataset[1:]
        self.batch_size = batch_size
        self.data_size = len(self.xs)
        # バッチの各サンプルの読み込み開始位置
        jump = self.data_size // batch_size
        self.offsets = [i * jump for i in range(batch_size)]

        self.reset()

    def reset(self):
        self.epoch = 0
        self.is_new_epoch = False
        self.iteration = 0
        self.time_idx = 0

    def __iter__(self):
        return self

    def next(self):
        batch_x = np.empty((self.batch_size), dtype='i')
        batch_t = np.empty((self.batch_size), dtype='i')

        time_idx, data_size = self.time_idx, self.data_size
        for i, offset in enumerate(self.offsets):
            batch_x[i] = self.xs[(offset + time_idx) % data_size]
            batch_t[i] = self.ts[(offset + time_idx) % data_size]

        self.time_idx += 1
        self.iteration += 1

        epoch = self.iteration * self.batch_size // self.data_size
        self.is_new_epoch = self.epoch < epoch
        if self.is_new_epoch:
            self.epoch = epoch

        return batch_x, batch_t

    def next(self):
        return self.__next__()