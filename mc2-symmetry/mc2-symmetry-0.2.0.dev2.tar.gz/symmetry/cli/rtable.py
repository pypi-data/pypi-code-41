import time
from typing import List

import pymq
import redis
from pymq.provider.redis import RedisConfig

from symmetry.api import RoutingRecord
from symmetry.common import config
from symmetry.common.shell import Shell, parsed, ArgumentError
from symmetry.routing import RedisRoutingTable


class RoutingUpdateListener:
    updates = list()

    def __init__(self, table) -> None:
        self.table = table
        pymq.subscribe(self._on_update)

    def _on_update(self, event: RoutingRecord):
        self.updates.append((time.gmtime(), self.table.get_routing(event.service)))


class RouterShell(Shell):
    prompt = 'rtbl> '

    def __init__(self, rds: redis.Redis):
        super().__init__()
        self.rds = rds
        self.table = RedisRoutingTable(rds)
        self.listener = RoutingUpdateListener(self.table)

    def do_info(self, _):
        self.println('connected to', self.rds)

    def do_list(self, _):
        records = [self.table.get_routing(service) for service in self.table.list_services()]

        self.print_table(records)

    def do_updates(self, _):
        for t, record in self.listener.updates:
            self.println(time.strftime('%Y-%m-%d %H:%M:%S', t), record)

    def do_flush(self, _):
        self.listener.updates.clear()

    @parsed
    def do_set(self, service, hosts, weights):
        """
        Set a routing record. For example

            set squeezenet heisenberg:8080,einstein:8080 1,2

        will set two hosts for the service squeezenet that are balanced at a ratio of 1 to 2

        :param service: the service name
        :param hosts: a comma separated list of hosts
        :param weights: a comma separated list of weights
        """
        hosts = [item.strip() for item in hosts.split(',')]

        try:
            weights = [float(item.strip()) for item in weights.split(',')]
        except ValueError as e:
            raise ArgumentError('Error while converting weights: %s' % e)

        if len(hosts) != len(weights):
            raise ArgumentError('Length of weights must equal population')

        record = RoutingRecord(service, hosts, weights)
        self.table.set_routing(record)
        self.println('ok', str(record))

    @parsed
    def do_unset(self, service: str):
        self.table.remove(service)

    @parsed
    def do_clear(self):
        """
        Removes all routing entries from the table
        """
        self.table.clear()

    def print_table(self, records: List[RoutingRecord]):
        println = self.println

        w = [-25, 20, 9]  # TODO: read from records

        sep = ['-' * abs(i) for i in w]
        sep = '+-' + '-+-'.join(sep) + '-+'

        row_fmt = ['%%%ds' % w[i] for i in range(len(w))]
        row_fmt = '| ' + ' | '.join(row_fmt) + ' |'

        header = ('Service', 'Hosts', 'Weights')

        println(sep)
        println(row_fmt % header)
        println(sep)

        for record in records:
            for i in range(len(record.hosts)):
                ls = (record.service if i == 0 else '', record.hosts[i], record.weights[i])
                println(row_fmt % ls)
            println(sep)


def main():
    rds = config.get_redis()
    pymq.init(RedisConfig(rds))

    shell = RouterShell(rds)
    shell.run()


if __name__ == '__main__':
    main()
