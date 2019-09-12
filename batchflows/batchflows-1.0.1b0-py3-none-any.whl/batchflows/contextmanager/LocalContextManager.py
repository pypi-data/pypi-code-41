from batchflows.contextmanager.ContextManager import ABCContextManager
from batchflows.util.JsonUtils import DateTimeEncoder, DateTimeDecoder
import os
import json
from threading import RLock


class FileContextManager(ABCContextManager):
    def __init__(self, file_location: str):
        super().__init__()
        self.file_location = file_location
        self.final_name = None
        self.save_lock = RLock()

    def remove(self):
        if os.path.exists(self.final_name):
            os.remove(self.final_name)

    def make_dirs(self):
        if not os.path.exists(self.file_location):
            os.makedirs(self.file_location)

    def load_from_external(self, batch_name: str):
        self.final_name = self.file_location + batch_name + '.json'

        if os.path.exists(self.final_name) and os.path.isfile(self.final_name):
            with open(self.final_name, "r") as json_file:
                loaded = json.load(json_file, cls=DateTimeDecoder)
                self.context = loaded['context']
                self.exec_map = loaded['exec_map']

            if super().is_batch_complete():
                self.context = dict()
                self.exec_map = None

    def save_progress(self, step_name: str = None, status: str = None):
        to_file = {
            'context': self.context,
            'exec_map': self.exec_map
        }

        self.save_lock.acquire()
        with open(self.final_name, 'w') as json_file:
            json.dump(to_file, json_file, cls=DateTimeEncoder)

        self.save_lock.release()

    def save_context(self):
        return None

    def save_batch_progress(self):
        self.save_progress(None, None)
