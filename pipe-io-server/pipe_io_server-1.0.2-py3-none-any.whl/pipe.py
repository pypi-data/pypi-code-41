from os import mkfifo, remove, chmod
from os.path import exists

DEFAULT_PERMISSIONS = 0o600


class Pipe:
    def __init__(self, path):
        self.path = path

    def recreate(self, permissions):
        self.remove()
        mkfifo(self.path)
        chmod(self.path, permissions)  # use chmod to ignore umask

    def remove(self):
        if exists(self.path):
            remove(self.path)
