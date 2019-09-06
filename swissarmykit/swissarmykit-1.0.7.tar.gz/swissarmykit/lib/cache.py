import json
import threading
import time

from swissarmykit.lib.core import Singleton


@Singleton
class Cache:
    data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)

    def set_group(self, group, key, value):
        if group in self.data.keys():
            self.data.get(group)[key] = value
        else:
            self.data[group] = {key: value}

    def get_group(self, group, key):
        return self.data.get(group).get(key)

    def is_exist_key_group(self, group, key):
        return group in self.data.keys() and key in self.data.get(group).keys()

    def __str__(self):
        return vars(self)

@Singleton
class CacheHtml:

    def init(self, lst):
        self.lst = lst
        self.MAX_LOAD = 200

        self.html = {}
        self.cursor_prev = 0
        self.cursor = 0
        self.stop_point = len(lst)

        self.data = []
        self.data_2 = []

        # Init the first CacheHtml.MAX_LOAD items. Default 200 item
        self.load_more_html()


    def should_load_html(self):
        return len(self.html) <= self.MAX_LOAD - 100 and self.cursor < self.stop_point

    def load_more_html(self):
        if self.should_load_html(): # re-check
            end = self.cursor + self.MAX_LOAD
            for item in self.lst[self.cursor:end]:
                self.html[item.id] = item.get_html()

            self.cursor = end

            print('INFO: Load more html at index:%d, total:%d' % (self.cursor, len(self.html)))

    def get(self, id):
        if self.should_load_html():
            self.load_more_html()

        while not self.html.get(id, None):
            time.sleep(1)
            print('%', end='', flush=True)

        return self.html.pop(id)

    def save(self, item):
        self.data.append(item)

    def save_2(self, item):
        self.data_2.append(item)

    def flush_database(self, fields=['data']):
        if self.data:
            data = self.data
            self.data = []
            for item in data:
                item.data = json.dumps(item.data)

            data[0].bulk_update(data, fields=fields)

        # if self.data_2:
        #     data = self.data_2
        #     self.data_2 = []
        #     data[0].bulk_update(data, fields=fields)
        print('INFO: Flush to database')
