import json
import os

from typing import Dict
from git_dependency_python.tools import create_dir


class DependencyLockManager:
    """
    Manager class working with a global dependency lock object file.
    """
    LOCK_FILE_PATH = '/tmp/git-dependecy-python/dependencies.lock'

    def __init__(self, create=False):
        # type: (bool) -> None
        """
        Contructor.

        :param create: Tells whether to create a new file or just open it.
        
        :return: No return.
        """
        if create:
            create_dir(self.LOCK_FILE_PATH)
            self.file = open(self.LOCK_FILE_PATH, 'w+')
            self.file.write('{}')
        else:
            self.file = open(self.LOCK_FILE_PATH, 'r+')

    def read(self):
        # type: () -> Dict[str, str]
        """
        Reads dependencies from lock file.
        
        :return: Dependencies dictionary.
        """
        self.file.seek(0)
        return json.loads(self.file.read())

    def update(self, data):
        # type: (Dict[str, str]) -> None
        """
        Updates dependencies to a lock file.
        
        :return: No return.
        """
        self.file.seek(0)
        self.file.write(json.dumps(data))
        self.file.truncate()

    def __del__(self):
        # type: () -> None
        """
        Deletes itself, closes opened lock file.
        
        :return: No return.
        """
        try:
            self.file.close()
        except Exception:
            pass

    def remove(self):
        # type: () -> None
        """
        Deletes file.

        :return: No return.
        """
        try:
            self.file.close()
            os.remove(self.LOCK_FILE_PATH)
        except Exception:
            pass
