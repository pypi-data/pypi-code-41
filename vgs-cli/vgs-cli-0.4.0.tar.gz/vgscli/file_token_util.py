import tempfile
import os

from vgscli.utils import is_file_accessible, eprint


class FileTokenUtil:

    def __init__(self, token_file_name):
        temp_dir = tempfile.gettempdir()
        self.temp_file = os.path.join(temp_dir, token_file_name)

    def read_token(self):
        with open(self.temp_file, 'r+') as tmp:
            return tmp.read()

    def write_token(self, token):
        with open(self.temp_file, 'w+') as tmp:
            tmp.write(token)
        return token

    def remove_token(self):
        if is_file_accessible(self.temp_file, 'r+'):
            os.remove(self.temp_file)
        else:
            eprint("No authenticated session", fatal=True)
