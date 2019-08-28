import time
import logging

from bmcsf.commands.base import Command
from bmcsf.services.backup import BackupService
from bmcsf.services.json_storage import JsonStorage
from bmcsf.services.ssh import SshService
from bmcsf.services.vultr import VultrService


class UpCommand(Command):
    def __init__(self):
        self.json_storage = JsonStorage()

    def handle(self, args):
        alias = args.alias
        storage_key = 'SERVER_{}'.format(alias)

        if not self.json_storage.has('SSHKEYID'):
            logging.error('Please configure MCSF first.')
            exit(1)

        vultr = VultrService()

        if self.json_storage.has(storage_key):
            logging.error('This alias is in use.')
            exit(2)

        logging.info('Creating new server ...')
        sub_id = vultr.start_new_server()
        self.json_storage.set(storage_key, sub_id)

        logging.info('Waiting server to get online ...')
        server = {}
        while True:
            try:
                server = vultr.get_server_info(sub_id)
                time.sleep(5)
                if server['main_ip'] == '0.0.0.0':
                    continue
            except KeyError:
                continue

            break

        logging.info('Connecting to server ...')

        ssh = SshService(server['main_ip'])
        backup_service = BackupService(alias, ssh)

        logging.info('Installing Java Runtime Environment ...')
        ssh.exec('apt-get update')
        ssh.exec('apt-get install -y default-jre')
        logging.info('Installing unzip ...')
        ssh.exec('apt-get install -y zip unzip')

        if backup_service.has_backup():
            logging.info('Restoring backup ...')
            backup_service.restore()
        else:
            logging.info('Downloading Minecraft server ...')
            ssh.exec('wget https://launcher.mojang.com/v1/objects/3dc3d84a581f14691199cf6831b71ed1296a9fdf/server.jar')
            logging.info('Running the server first time ...')
            ssh.exec('java -Xmx1024M -Xms1024M -jar server.jar nogui')
            logging.info('Accepting EULA ...')
            ssh.exec("sed -i 's/false/true/g' eula.txt")
            logging.info('Installation completed.')

        logging.info('Starting Minecraft server ...')
        ssh.exec('nohup java -Xmx1024M -Xms1024M -jar server.jar nogui &')

        logging.info('Connect to server:')
        logging.info('{}:{}'.format(server['main_ip'], 25565))
        logging.info('Please wait while server is initializing!')
