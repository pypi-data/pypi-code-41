import configparser
from sys import platform
from pathlib import Path


class Connect:
    def __init__(self, source):
        if platform == 'linux':
            path_to_secrets = Path(f'{Path.home()}/prime_secrets')
            self.secrets_path = path_to_secrets
        elif platform == 'win32':
            self.secrets_path = r'C:\Users\Datasoft\prime_secrets'
        else:
            self.secrets_path = ''

        self.config = configparser.ConfigParser()
        self.config.read(self.secrets_path)
        self.user_name = self.config.get(source, "user_name")
        self.password = self.config.get(source, "password")

    def __repr__(self):
        return f'Username: {self.user_name}, password: {self.password}'
