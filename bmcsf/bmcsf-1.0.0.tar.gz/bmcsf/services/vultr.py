from os import environ
from vultr import Vultr

from bmcsf.services.json_storage import JsonStorage


class VultrService:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = environ.get('VULTR_KEY', None)

        self.api_key = api_key
        self.vultr = Vultr(api_key)
        self.json_storage = JsonStorage()

    def list_os(self):
        return self.vultr.os.list()

    def list_regions(self):
        return self.vultr.regions.list()

    def list_vps_plans(self):
        return self.vultr.plans.list()

    def create_new_ssh_key(self, public_key):
        assert self.api_key is not None

        return self.vultr.sshkey.create('bmcsf', public_key)['SSHKEYID']

    def get_server_info(self, sub_id):
        assert self.api_key is not None

        return self.vultr.server.list()[sub_id]

    def start_new_server(self):
        assert self.api_key is not None

        return self.vultr.server.create(
            self.json_storage.get('selected_region'),
            self.json_storage.get('selected_plan'),
            self.json_storage.get('selected_os'),
            {
                'SSHKEYID': self.json_storage.get('SSHKEYID'),
                'enable_ipv6': 'yes',
                'hostname': 'bmcsf'
            }
        )['SUBID']

    def delete_server(self, subid):
        assert self.api_key is not None

        return self.vultr.server.destroy(subid)
