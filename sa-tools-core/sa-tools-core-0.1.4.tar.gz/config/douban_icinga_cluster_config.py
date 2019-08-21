# coding: utf-8

import logging
import requests

from sa_tools_core.libs.icinga import IcingaClusterConfig

logger = logging.getLogger(__name__)


class DoubanIcingaClusterConfig(IcingaClusterConfig):
    ICINGA_SHIP_TAGS = ('icinga_master', 'icinga_checker')
    NAGBOT_LINK = 'http://nb.douban.com/link/'
    ICINGA_LINK = 'http://icinga.intra.douban.com/icingaweb2/monitoring/service/show?host=${host}&service=${service}'
    SHIP_TAG = 'http://sysadmin.douban.com/ship/search/?pattern={tag}'

    LINK_TYPE_ACK = 1
    LINK_TYPE_REBOOT_HOST = 2

    @classmethod
    def get_link_by_type(cls, env, _type):
        if (env.HOSTSTATE == 'UP'
                or env.SERVICESTATE == 'OK'
                or env.NAGIOS_NOTIFICATIONTYPE == 'ACKNOWLEDGEMENT'):
            return None

        data = {
            'host': env.NAGIOS_HOSTNAME,
            'service': env.NAGIOS_SERVICEDESC,
            'user': env.NAGIOS_CONTACTNAME,
            'ack_type': _type,
            'is_icinga': 1,
        }
        try:
            resp = requests.post(cls.NAGBOT_LINK, data=data)
            return resp.text.strip()
        except Exception:
            logger.exception('get ack link fail')
            return None

    @classmethod
    def get_ack_link(cls, env):
        return cls.get_link_by_type(env, cls.LINK_TYPE_ACK)

    @classmethod
    def get_reboot_host_link(cls, env):
        try:
            if env.TARGET_TYPE == 'service':
                # service
                # if service.ssh.problem: duration >= 10min
                if env.NAGIOS_SERVICEDESC == 'ssh' and float(env.SERVICE_DURATION_SEC) >= 600:
                    return cls.get_link_by_type(env, cls.LINK_TYPE_REBOOT_HOST)
            else:
                # host
                # if host: duration >= 2min
                if env.HOST_DURATION_SEC and float(env.HOST_DURATION_SEC) >= 120:
                    return cls.get_link_by_type(env, cls.LINK_TYPE_REBOOT_HOST)
        except Exception:
            logger.exception('failed to get_reboot_host_link: ')
        return None

    @classmethod
    def get_icinga_link(cls, env):
        return cls.ICINGA_LINK.format(host=env.HOSTALIAS, service=env.SERVICEDESC)

    @classmethod
    def get_icinga_hosts(cls):
        return {'%s.intra.douban.com' % host
                for tag in cls.ICINGA_SHIP_TAGS
                for host in requests.get(cls.SHIP_TAG.format(tag=tag)).json()}
