from __future__ import annotations

from zabier.zabbix.action import ActionMixin
from zabier.zabbix.host import HostMixin
from zabier.zabbix.hostgroup import HostGroupMixin
from zabier.zabbix.template import TemplateMixin

zabbix = None


class Zabbix(ActionMixin, HostGroupMixin, TemplateMixin, HostMixin):
    pass


def configure(url: str, user_name: str, password: str):
    global zabbix
    zabbix = Zabbix(
        url=url,
        user_name=user_name,
        password=password)


def get_client():
    global zabbix
    if zabbix is None:
        raise Exception('Zabbix client is not configured.')
    zabbix.login()
    return zabbix
