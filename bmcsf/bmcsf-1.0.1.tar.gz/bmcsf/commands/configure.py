import logging

from bmcsf.commands.base import Command
from bmcsf.services.crypto import CryptoService
from bmcsf.services.json_storage import JsonStorage
from bmcsf.services.vultr import VultrService


class ConfigureCommand(Command):
    def __init__(self):
        self.vultr = VultrService()
        self.json_storage = JsonStorage()

    def handle(self, args):

        logging.info('Loading Vultr definitions ...')

        if not self.json_storage.has('v_os'):
            logging.info('Fetching operating systems ...')
            v_os = self.vultr.list_os()
            logging.info('Fetching regions ...')
            v_regions = self.vultr.list_regions()
            logging.info('Fetching VPS plans ...')
            v_plans = self.vultr.list_vps_plans()

            self.json_storage.set('v_os', v_os)
            self.json_storage.set('v_regions', v_regions)
            self.json_storage.set('v_plans', v_plans)

            logging.info('Done.')
        else:
            v_os = self.json_storage.get('v_os')
            v_regions = self.json_storage.get('v_regions')
            v_plans = self.json_storage.get('v_plans')

        print("Select a Operating System:")
        for _v_os in v_os.values():
            if 'ubuntu' not in _v_os['name'].lower():
                continue

            print("{} - {}".format(_v_os['OSID'], _v_os['name']))

        selected_os = input("> ")

        for v_region in v_regions.values():
            print("{} - {}".format(v_region['DCID'], v_region['name']))

        selected_region = input("> ")

        for v_plan in v_plans.values():
            print("{} - {}".format(v_plan['VPSPLANID'], v_plan['name']))

        selected_plan = input('> ')

        self.json_storage.set('selected_os', selected_os)
        self.json_storage.set('selected_region', selected_region)
        self.json_storage.set('selected_plan', selected_plan)

        if not self.json_storage.has('SSHKEYID'):
            logging.info('Generating SSH keys ...')

            crypto = CryptoService()
            public_key = crypto.get_public_key()
            key_id = self.vultr.create_new_ssh_key(public_key)
            self.json_storage.set('SSHKEYID', key_id)

        logging.info('Done.')
