# Copyright (C) 2019, AllWorldIT.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""BIRD client class."""

import re
import socket

from typing import Any, Dict, List, Optional

__version__ = '0.0.1'


class BirdClient:
    """BIRD client class."""

    # Socket file
    _socket_file: str
    # Ending lines for bird control channel
    _ending_lines: List[bytes]

    def __init__(self, socket_file: Optional[str] = None):
        """Initialize the object."""

        # Set socket file
        self._socket_file = socket_file
        # Setup ending lines
        self._ending_lines = (b'0000 ', b'0013 ', b'8001 ', b'8003 ', b'9001 ')

    def show_status(self, data: Optional[List[str]] = None) -> Dict[str, str]:
        """Return parsed BIRD status."""

        # Grab status
        if not data:
            data = self.query('show status')

        # Return structure
        res = {
            'version': '',
            'router_id': '',
            'server_time': '',
            'last_reboot': '',
            'last_reconfiguration': '',
        }

        # Loop with data to grab information we need
        for line in data:
            # Grab BIRD version
            match = re.match(r'^0001 BIRD (?P<version>[0-9\.]+) ready\.$', line)
            if match:
                res['version'] = match.group('version')
            # Grab Router ID
            match = re.match(r'^1011-Router ID is (?P<router_id>[0-9\.]+)$', line)
            if match:
                res['router_id'] = match.group('router_id')
            # Current server time
            match = re.match(r'^ Current server time is (?P<server_time>[0-9\.\s:\-]+)$', line)
            if match:
                res['server_time'] = match.group('server_time')
            # Last reboot
            match = re.match(r'^ Last reboot on (?P<last_reboot>[0-9\.\s:\-]+)$', line)
            if match:
                res['last_reboot'] = match.group('last_reboot')
            # Last reconfiguration
            match = re.match(r'^ Last reconfiguration on (?P<last_reconfig>[0-9\.\s:\-]+)$', line)
            if match:
                res['last_reconfiguration'] = match.group('last_reconfig')

        return res

    def show_protocols(self, data: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return parsed BIRD protocols."""

        # Grab protocols
        if not data:
            data = self.query('show protocols')

        res = {}

        # Loop with data to grab information we need
        for line in data:
            # Grab BIRD version
            match = re.match(r'^(?:1002-| )'
                             r'(?P<name>\S+)\s+'
                             r'(?P<proto>\S+)\s+'
                             r'(?P<table>\S+)\s+'
                             r'(?P<state>\S+)\s+'
                             r'(?P<since>\S+)\s+'
                             r'(?P<info>.*)', line)
            if match:
                # Build up the protocol
                protocol = {}
                protocol['name'] = match.group('name')
                protocol['proto'] = match.group('proto')
                protocol['table'] = match.group('table')
                protocol['state'] = match.group('state')
                protocol['since'] = match.group('since')
                protocol['info'] = match.group('info')
                # Save protocol
                res[protocol['name']] = protocol

        return res

    # pylama: ignore=R0915,C901
    def show_route_table(self, table: str, data: Optional[List[str]] = None) -> List:
        """Return parsed BIRD routing table."""

        # Grab routes
        if not data:
            data = self.query(f'show route table {table} all')

        res = []

        # Loop with data to grab information we need
        route: Dict[str, Any] = {}
        for line in data:
            # Grab a OSPF route
            match = re.match(r'^(?:1007-| )'
                             r'(?P<prefix>\S+)\s+'
                             r'(?P<type>\S+)\s+'
                             r'\[(?P<proto>\S+)\s+'
                             r'(?P<since>\S+)\]\s+'
                             r'(?P<ospf_type>(?:I|IA|E1|E2))?\s*'
                             r'\((?P<pref>\d+)/(?P<metric1>\d+)(?:/(?P<metric2>\d+))?\)'
                             r'(?:\s+\[(?P<tag>[0-9a-f]+)\])?'
                             r'(?:\s+\[(?P<router_id>[0-9\.]+)\])?', line)
            if match:
                # Build the route
                route = {}
                route['prefix'] = match.group('prefix')
                route['type'] = match.group('type')
                route['proto'] = match.group('proto')
                route['since'] = match.group('since')
                route['ospf_type'] = match.group('ospf_type')
                route['pref'] = match.group('pref')
                route['metric1'] = match.group('metric1')
                route['metric2'] = match.group('metric2')
                route['tag'] = match.group('tag')
                route['router_id'] = match.group('router_id')
                # Append route to our results
                res.append(route)
                continue

            # Grab a normal route
            match = re.match(r'^(?:1007-| )'
                             r'(?P<prefix>\S+)\s+'
                             r'(?P<type>\S+)\s+'
                             r'\[(?P<proto>\S+)\s+'
                             r'(?P<since>\S+)\]\s+'
                             r'(?P<primary>\*)?\s*'
                             r'\((?P<weight>\S+)\)', line)
            if match:
                # Build the route
                route = {}
                route['prefix'] = match.group('prefix')
                route['type'] = match.group('type')
                route['proto'] = match.group('proto')
                route['since'] = match.group('since')
                route['primary'] = match.group('primary')
                route['weight'] = match.group('weight')
                # Append the route to our results
                res.append(route)
                continue

            # Grab nexthop details via a gateway
            match = re.match(r'\s+via\s+'
                             r'(?P<gateway>\S+)\s+'
                             r'on (?P<interface>\S+)'
                             r'(?: mpls (?P<mpls>[0-9/]+))?'
                             r'(?: (?P<onlink>onlink))?'
                             r'(?: weight (?P<weight>[0-9]+))?', line)
            if match:
                # Build the nexthop
                if 'nexthops' not in route:
                    route['nexthops'] = []
                nexthop = {}
                nexthop['gateway'] = match.group('gateway')
                nexthop['interface'] = match.group('interface')
                nexthop['mpls'] = match.group('mpls')
                nexthop['onlink'] = match.group('onlink')
                nexthop['weight'] = match.group('weight')
                # Save gateway
                route['nexthops'].append(nexthop)
                continue

            # Grab nexthop details via a device
            match = re.match(r'\s+dev (?P<interface>\S+)'
                             r'(?: mpls (?P<mpls>[0-9/]+))?'
                             r'(?: (?P<onlink>onlink))?'
                             r'(?: weight (?P<weight>[0-9]+))?', line)
            if match:
                # Build the nexthop
                if 'nexthops' not in route:
                    route['nexthops'] = []
                nexthop = {}
                nexthop['interface'] = match.group('interface')
                nexthop['mpls'] = match.group('mpls')
                nexthop['onlink'] = match.group('onlink')
                nexthop['weight'] = match.group('weight')
                # Save gateway
                route['nexthops'].append(nexthop)
                continue

            # Grab type details
            match = re.match(r'1008-\s+'
                             r'Type: (?P<type>.*)', line)
            if match:
                # Work out the types
                if 'type' not in route:
                    route['type'] = []
                route_types = match.group('type').split()
                # Save type
                route['type'] = route_types
                continue

        return res

    def query(self, query: str) -> List[str]:
        """Open a socket to the BIRD daemon, send the query and get the response."""

        # Create a unix socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Connect to the BIRD daemon
        sock.connect(self._socket_file)

        # Send the query
        sock.send(f'{query}\n'.encode('ascii'))

        # Initialize byte array to store what we get back
        data = bytearray()

        # Loop while we're not done
        done = False
        while not done:
            chunk = sock.recv(10)
            data.extend(chunk)
            # If the last bit of data ends us off in a newline, this may be the end of the stream
            if data.endswith(b'\n'):
                # Check by splitting the lines off
                lines = data.splitlines()
                # Grab last line
                last_line = lines[-1]
                # Check if this is an ending line
                for ending in self._ending_lines:
                    # If it is, then we're done
                    if last_line.startswith(ending):
                        done = True
        # Close socket
        sock.close()

        # Convert data bytes to a string and split into lines
        return data.decode('ascii').splitlines()
