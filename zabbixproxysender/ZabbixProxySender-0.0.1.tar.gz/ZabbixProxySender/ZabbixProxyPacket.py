from datetime import datetime
import json


class ZabbixProxyPacket:
    def __init__(self, proxyName):
        self.proxyName = proxyName
        self.clean()

    def __str__(self):
        return json.dumps(self.packet)

    def add(self, host, key, value, clock=datetime.now().timestamp()):
        if (isinstance(clock, int)) or (isinstance(clock, float)):
            metric = {'host': str(host),
                      'key': str(key),
                      'value': str(value),
                      'clock': int(clock)}
        else:
            raise TypeError('Clock must be unixtime')

        self.packet['data'].append(metric)

    def clean(self):
        self.packet = {'request': 'history data',
                       'host': self.proxyName,
                       'data': []}
