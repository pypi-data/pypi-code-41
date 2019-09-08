import copy

import jinja2

from unv.app.settings import ComponentSettings, SETTINGS as APP_SETTINGS
from unv.deploy.components.redis import SETTINGS as REDIS_DEPLOY_SETTINGS
from unv.deploy.settings import SETTINGS as DEPLOY_SETTINGS


class WebSettings(ComponentSettings):
    KEY = 'web'
    SCHEMA = {
        'autoreload': {'type': 'boolean', 'required': True},
        'jinja2': {
            'type': 'dict',
            'required': True,
            'schema': {
                'enabled': {'type': 'boolean', 'required': True}
            }
        },
        'redis': {
            'type': 'dict',
            'schema': {
                'enabled': {'type': 'boolean', 'required': True},
                'connections': {
                    'type': 'dict',
                    'required': True,
                    'schema': {
                        'min': {'type': 'integer', 'required': True},
                        'max': {'type': 'integer', 'required': True}
                    }
                },
                'host': {'type': 'string', 'required': False},
                'port': {'type': 'integer', 'required': False},
                'database': {'type': 'integer', 'required': True}
            }
        }
    }
    DEFAULT = {
        'autoreload': False,
        'jinja2': {'enabled': True},
        'redis': {
            'enabled': False,
            'connections': {'min': 10, 'max': 50},
            'database': 0
        }
    }

    @property
    def jinja2_enabled(self):
        return self._data['jinja2']['enabled']

    @property
    def jinja2_settings(self):
        settings = copy.deepcopy(self._data.get('jinja2', {}))
        settings.pop('enabled')
        settings['enable_async'] = True
        settings['loader'] = jinja2.ChoiceLoader([
            jinja2.PackageLoader(component.__name__)
            for component in APP_SETTINGS.get_components()
        ])
        if 'jinja2.ext.i18n' not in settings.setdefault('extensions', []):
            settings['extensions'].append('jinja2.ext.i18n')
        return settings

    @property
    def redis_host(self):
        hosts = list(DEPLOY_SETTINGS.get_hosts('redis'))
        host = hosts[0][1]['private_ip'] if hosts else ''
        return self._data['redis'].get('host', host)

    @property
    def redis_port(self):
        return self._data['redis'].get('port', REDIS_DEPLOY_SETTINGS.port)

    @property
    def redis_enabled(self):
        return self._data['redis']['enabled']

    @property
    def redis_database(self):
        return self._data['redis']['database']

    @property
    def redis_min_connections(self):
        return self._data['redis']['connections']['min']

    @property
    def redis_max_connections(self):
        return self._data['redis']['connections']['max']


SETTINGS = WebSettings()
