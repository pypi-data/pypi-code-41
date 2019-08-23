import time

class Journal (object):
    def __init__(self, type, data, action):
        self.type = type
        self.datatime = time.time()
        self.action = action
        self.data = data
