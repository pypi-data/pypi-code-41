import logging

from vultr import VultrError

from bmcsf.commands.base import Command
from bmcsf.services.backup import BackupService
from bmcsf.services.json_storage import JsonStorage
from bmcsf.services.ssh import SshService
from bmcsf.services.vultr import VultrService


class DownCommand(Command):
    def __init__(self):
        self.json_storage = JsonStorage()

    def handle(self, args):
        alias = args.alias
        storage_key = 'SERVER_{}'.format(alias)

        if not self.json_storage.has('SSHKEYID'):
            logging.error('Please configure MCSF first.')
            exit(1)

        vultr = VultrService()

        if not self.json_storage.has(storage_key):
            logging.error('This alias is in use.')
            exit(3)

        sub_id = self.json_storage.get(storage_key)
        if sub_id is None:
            logging.error('Could not find the sub id of the server, exiting.')
            exit(4)

        logging.info('Backing up ...')

        logging.info('Getting server info ...')
        server = vultr.get_server_info(sub_id)

        ssh = SshService(server['main_ip'])
        backup_service = BackupService(alias, ssh)

        logging.info('Stopping Minecraft server ...')
        ssh.exec('killall java')

        backup_service.backup()
        logging.info('Backup is completed.')

        logging.info('Destroying server on Vultr ...')

        try:
            vultr.delete_server(sub_id)
        except VultrError:
            logging.warning('Server is already removed on Vultr.')

        self.json_storage.remove(storage_key)
        logging.info('Done.')
