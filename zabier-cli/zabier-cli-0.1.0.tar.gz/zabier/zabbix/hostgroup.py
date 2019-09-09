from dataclasses import asdict, dataclass
from typing import Dict, Optional

from zabier.zabbix.base import ZabbixBase


@dataclass
class HostGroup:
    groupid: str
    name: str


class HostGroupMixin(ZabbixBase):
    def create_host_group(self, hostgroup: HostGroup) -> int:
        params = asdict(hostgroup)
        del params['groupid']
        response: Dict = self.do_request("hostgroup.create", params)
        return response['result']['groupids'].pop()

    def host_group_exists(self, name: str) -> bool:
        return self.get_host_group_by_name(name) is not None

    def get_host_group_by_name(self, name: str) -> Optional[HostGroup]:
        response: Dict = self.do_request(
            "hostgroup.get",
            {
                "search": {
                    "name": [name]
                },
                "editable": True,
                "startSearch": True,
                "searchByAny": True
            }
        )
        if len(response['result']) == 0:
            return None
        hostgroup = response['result'].pop()
        return HostGroup(
            groupid=hostgroup['groupid'],
            name=hostgroup['name'])
