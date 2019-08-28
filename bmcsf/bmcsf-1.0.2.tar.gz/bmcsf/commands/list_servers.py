import logging

from bmcsf.commands.base import Command
from bmcsf.services.json_storage import JsonStorage


class ListCommand(Command):
    def __init__(self):
        self.json_storage = JsonStorage()

    def handle(self, args):
        if not self.json_storage.has('SSHKEYID'):
            logging.error('Please configure MCSF first.')
            exit(1)

        server_keys = filter(lambda x: x.startswith('SERVER_'), list(self.json_storage.data.keys()))

        for server_key in server_keys:
            print(" * ", server_key.split("_")[-1])
