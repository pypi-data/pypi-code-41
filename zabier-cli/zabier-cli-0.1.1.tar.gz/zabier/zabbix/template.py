import json
from dataclasses import dataclass
from typing import Dict, Optional

from zabier.zabbix.base import ZabbixBase


@dataclass
class Template:
    templateid: Optional[str]
    host: str
    name: str
    description: str


class TemplateMixin(ZabbixBase):
    def get_template_by_name(self, name: str) -> Optional[Template]:
        response: Dict = self.do_request(
            'template.get',
            {
                'filter': {
                    'name': [name]
                },
                'editable': True,
                'startSearch': True,
                'searchByAny': True
            }
        )
        if len(response['result']) == 0:
            return None
        template = response['result'].pop()
        return Template(
            templateid=template['templateid'],
            host=template['host'],
            name=template['name'],
            description=template['description'])

    def import_template_configuration(self,
                                      config: Dict) -> bool:
        response: Dict = self.do_request(
            'configuration.import',
            {
                'format': 'json',
                'rules': {
                    'templates': {
                        'createMissing': True,
                        'updateExisting': True
                    },
                    'applications': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'discoveryRules': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'graphs': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'items': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'templateLinkage': {
                        'createMissing': True
                    },
                    'templateScreens': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'triggers': {
                        'createMissing': True,
                        'updateExisting': True,
                        'deleteMissing': True
                    },
                    'valueMaps': {
                        'createMissing': True,
                        'updateExisting': True
                    }
                },
                'source': json.dumps(config)
            }
        )
        return response['result']

    def export_template_configuration(self, template_id: str) -> bool:
        response: Dict = self.do_request(
            'configuration.export',
            {
                'format': 'json',
                'options': {
                    'templates': [template_id]
                }
            }
        )
        return response['result']
