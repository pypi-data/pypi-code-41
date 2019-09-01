# -*- coding: utf-8 -*-
import time


class UpdateTimer(object):
    def __init__(self, interval=None):
        interval = 1. if interval is None else interval
        self.__interval = interval
        self.__start_time = None

    def update_if_possible(self, do_update):
        now = time.time()
        if self.__start_time is None or now - self.__start_time >= self.__interval:
            self.__start_time = now
            do_update()
