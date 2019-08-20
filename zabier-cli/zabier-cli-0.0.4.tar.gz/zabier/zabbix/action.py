from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from dacite import from_dict

from zabier.zabbix.base import ZabbixBase


@dataclass
class Action:
    actionid: Optional[str]
    name: str
    esc_period: str
    eventsource: str
    status: str
    operations: List[Dict]
    filter: Dict


class ActionMixin(ZabbixBase):
    def get_action_by_name(self, name: str) -> Optional[Action]:
        response: Dict = self.do_request(
            'action.get',
            {
                'search': {
                    'name': [name]
                },
                'editable': True,
                'startSearch': True,
                'searchByAny': True,
                'selectOperations': 'extend',
                'selectFilter': 'extend'
            }
        )
        if len(response['result']) == 0:
            return None
        action = response['result'].pop()
        return from_dict(data_class=Action, data=action)

    def create_action(self, action: Action) -> int:
        response: Dict = self.do_request(
            'action.create',
            asdict(action))
        return response['result']['actionids'].pop()

    def update_action(self, action: Action) -> int:
        action_dict = asdict(action)
        del action_dict['eventsource']
        response: Dict = self.do_request(
            'action.update',
            action_dict)
        return response['result']['actionids'].pop()
