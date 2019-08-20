import json
from dataclasses import dataclass
from typing import Dict, Optional

from zabier.zabbix.base import ZabbixBase


@dataclass
class Host:
    hostid: Optional[str]


class HostMixin(ZabbixBase):
    def get_host_by_name(self, name: str) -> Optional[Host]:
        response: Dict = self.do_request(
            'host.get',
            {
                'search': {
                    'name': [name]
                },
                'editable': True,
                'startSearch': True,
                'searchByAny': True
            }
        )
        if len(response['result']) == 0:
            return None
        host = response['result'].pop()
        return Host(hostid=host['hostid'])

    def import_host_configuration(self,
                                  config: Dict) -> bool:
        response: Dict = self.do_request(
            'configuration.import',
            {
                'format': 'json',
                'rules': {
                    'templates': {
                        'createMissing': True,
                        'updateExisting': True
                    }
                },
                'source': json.dumps(config)
            }
        )
        return response['result']

    def export_host_configuration(self, host_id: str) -> bool:
        response: Dict = self.do_request(
            'configuration.export',
            {
                'format': 'json',
                'options': {
                    'hosts': [host_id]
                }
            }
        )
        return response['result']
