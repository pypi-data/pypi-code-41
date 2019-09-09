# -*- coding: utf-8 -*-
"""Domain Driven Design framework."""
import os
from ddd_base import Aggregate
from .block import Block, TEMPLATE_DIR
from .server import Server
from .upstream import Upstream
from .map import Map
from .location import Location
from .exception import NginxError
from .file_manager import make_dir, create_file, copy_file


class Nginx(Aggregate, Block):

    def __init__(self, host):
        super().__init__()
        self._namespace = None
        self.host = host
        self.maps = []
        self.upstreams = []
        self.locations = []
        self.servers = []

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        self._namespace = value + '.' + self.host

    def _dump_map(self):
        def map_dump(the_map):
            return the_map.dump("map.conf.jinja2", {
                "key_name": the_map.definition.key,
                "value_name": the_map.definition.value,
                "key_pairs": the_map.key_pairs
            })

        return [map_dump(a_map) for a_map in self.maps]

    def _dump_upstream(self):
        def map_upstream(the_upstream):
            return the_upstream.dump("upstream.conf.jinja2", {
                "name": the_upstream.name,
                "servers": the_upstream.servers,
            })

        return [map_upstream(a_upstream) for a_upstream in self.upstreams]

    def _dump_location(self):
        def map_location(the_location):
            return the_location.dump("location.conf.jinja2", {
                "name": the_location.name,
                "proxy": the_location.proxy,
                "variables": the_location.sets,
                "scope": the_location.scope
            })

        return [map_location(a_location) for a_location in self.locations]

    def _dump_server(self):
        def map_server(the_server):
            return the_server.dump("server-location.conf.jinja2", {
                "name": the_server.name,
                "variables": the_server.sets,
                "locations": the_server.locations,
            })

        return [map_server(a_server) for a_server in self.servers]

    def _dump_nginx(self):
        return self.dump("nginx.conf.jinja2", {
            "namespace": self.namespace,
        })

    @staticmethod
    def _generate_conf(directory, configs, name):
        for idx, a_config in enumerate(configs):
            create_file(os.path.join(directory, str(idx) + '_' + name + '.conf'), a_config)

    def dumps(self, directory):
        make_dir(directory)
        maps = self._dump_map()
        upstreams = self._dump_upstream()
        locations = self._dump_location()
        servers = self._dump_server()
        nginx = self._dump_nginx()

        self._generate_conf(directory, maps, 'map')
        self._generate_conf(directory, upstreams, 'upstream')
        location_dir = os.path.join(directory, "locations_conf.d")
        make_dir(location_dir)
        self._generate_conf(location_dir, locations, 'location')
        self._generate_conf(directory, servers, 'server')
        create_file(os.path.join(directory, "root.conf"), nginx)

        copy_file(
            os.path.join(TEMPLATE_DIR, "error_page.conf"),
            os.path.join(directory, "error_page.conf"))

        all_in_one = self.dump("all-in-one.conf.jinja2", {
            "namespace": self.namespace,
            "maps": maps,
            "upstreams": upstreams,
            "servers": servers,
        })
        create_file(os.path.join(directory, "all-in-one.conf"), all_in_one)

    def append(self, block):
        if isinstance(block, Server):
            self.servers.append(block)
        elif isinstance(block, Map):
            self.maps.append(block)
        elif isinstance(block, Upstream):
            self.upstreams.append(block)
        elif isinstance(block, Location):
            self.locations.append(block)
            self.servers[0].append(block)
        else:
            raise NginxError()
