import ipaddress
from typing import Optional, List

import yaml

from .network import HostGroup, Host


class Config(object):

    def __init__(self, config_file: str):

        self._hosts = {}
        self._static_hosts = {}
        self.network_prefixes = {}
        self._aliases = {}

        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)

            for host_group_entry in data_loaded['hostgroups']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self._hosts.update({host.ipv4_address: host for host in host_group.hosts()})

            for host_group_entry in data_loaded['hosts']:
                host_group = self.create_host_group(host_group_entry)

                for host_entry in host_group_entry['hosts']:
                    self.map_entry(host_entry, host_group)

                self._static_hosts.update({host.ipv4_address: host for host in host_group.hosts()})

            for host in self.all_hosts:
                for alias in host.aliases:
                    self._aliases[alias] = host

    def create_host_group(self, host_group_entry):
        prefix_ = host_group_entry['prefix']
        cidr_ = host_group_entry['cidr']
        self.network_prefixes[cidr_] = prefix_
        host_group = HostGroup(prefix_, cidr_)
        return host_group

    def map_entry(self, host_entry, host_group):
        offset_ = host_entry['offset']
        count_ = host_entry['count'] if 'count' in host_entry else 1

        if 'alias' in host_entry:
            aliases_ = (host_entry['alias'],)
        elif 'aliases' in host_entry:
            aliases_ = tuple(host_entry['aliases'])
        else:
            aliases_ = None

        if 'config' in host_entry:
            config_ = [(config_entry['source'], config_entry['target']) for config_entry in host_entry['config']]
        else:
            config_ = None

        image_type_ = host_entry['image_type'] if 'image_type' in host_entry else None

        host_group.add_hosts(offset_, count_, aliases_, image_type_, config_)

    @property
    def hosts(self) -> List[Host]:
        return list(self._hosts.values())

    @property
    def static_hosts(self) -> List[Host]:
        return list(self._static_hosts.values())

    @property
    def all_hosts(self) -> List[Host]:
        return self.hosts + self.static_hosts

    @property
    def aliases(self):
        aliases = []
        for alias, host in self._aliases.items():
            aliases.append((alias, host.host_name))
        return aliases

    @property
    def netboot_ip(self):
        return self.alias('netboot').ipv4_address

    def alias(self, alias):
        return self._aliases[alias] if alias in self._aliases else None

    def get_host(self, ip_address_string: str) -> Optional[Host]:
        if ip_address_string in self._static_hosts:
            return self._static_hosts[ip_address_string]

        if ip_address_string in self._hosts:
            return self._hosts[ip_address_string]

        ip_address = ipaddress.IPv4Address(ip_address_string)
        for cidr, prefix in self.network_prefixes.items():
            network = ipaddress.IPv4Network(cidr)
            if ip_address in network:
                return Host(prefix, network, ip_address)
        return None

    def render_hosts(self):
        lines = []

        lines.append("127.0.0.1\tlocalhost")
        lines.append("::1\tlocalhost ip6-localhost ip6-loopback")
        lines.append("fe00::0\tip6-localnet")
        lines.append("ff00::0\tip6-mcastprefix")
        lines.append("ff02::1\tip6-allnodes")
        lines.append("ff02::2\tip6-allrouters")
        lines.append("ff02::3\tip6-allhosts")

        lines.append("")

        for host in self.all_hosts:
            lines.append(host.entry)

        return "\n".join(lines)
