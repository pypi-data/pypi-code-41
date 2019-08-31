#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml
import os
import re
import errno
import click
from logging import debug, warning, error
from .node import *
from jinja2 import Environment, PackageLoader
from collections import defaultdict

import contextlib

# Constructed with help from
# http://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
# Try it on regex101: https://regex101.com/r/yVdrJQ/1
# See https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8
IPV4SEG  = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'\.){3,3}' + IPV4SEG + r')'
IPV6SEG  = r'(?:(?:[0-9a-fA-F]){1,4})'
IPV6GROUPS = (
    r'(?:' + IPV6SEG + r':){7,7}' + IPV6SEG,                  # 1:2:3:4:5:6:7:8
    r'(?:' + IPV6SEG + r':){1,7}:',                           # 1::                                 1:2:3:4:5:6:7::
    r'(?:' + IPV6SEG + r':){1,6}:' + IPV6SEG,                 # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
    r'(?:' + IPV6SEG + r':){1,5}(?::' + IPV6SEG + r'){1,2}',  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
    r'(?:' + IPV6SEG + r':){1,4}(?::' + IPV6SEG + r'){1,3}',  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
    r'(?:' + IPV6SEG + r':){1,3}(?::' + IPV6SEG + r'){1,4}',  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
    r'(?:' + IPV6SEG + r':){1,2}(?::' + IPV6SEG + r'){1,5}',  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
    IPV6SEG + r':(?:(?::' + IPV6SEG + r'){1,6})',             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
    r':(?:(?::' + IPV6SEG + r'){1,7}|:)',                     # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
    r'fe80:(?::' + IPV6SEG + r'){0,4}%[0-9a-zA-Z]{1,}',       # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,     # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,          # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)
IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])  # Reverse rows for greedy match


@contextlib.contextmanager
def smart_open(filename: str, mode: str = 'r', *args, **kwargs):
    '''Open files and i/o streams transparently.'''
    if filename == '-':
        if 'r' in mode:
            stream = sys.stdin
        else:
            stream = sys.stdout
        if 'b' in mode:
            fh = stream.buffer  # type: IO
        else:
            fh = stream
        close = False
    else:
        fh = open(filename, mode, *args, **kwargs)
        close = True

    try:
        yield fh
    finally:
        if close:
            try:
                fh.close()
            except AttributeError:
                pass

DEFAULT_FILENAME='docker-compose.yml'

env = Environment(
    loader=PackageLoader('ccompose', 'templates'),
    comment_start_string='{##',
    comment_end_string='##}',
)

def dep_resolve(node, resolved, unresolved):
   unresolved.append(node)
   for edge in node.edges:
      if edge not in resolved:
         if edge in unresolved:
            raise Exception('Circular reference detected: %s -> %s' % (node.name, edge.name))
         dep_resolve(edge, resolved, unresolved)
   resolved.append(node)
   unresolved.remove(node)

# "Batches" are sets of tasks that can be run together
# This has been borrowed from https://breakingcode.wordpress.com/2013/03/11/an-example-dependency-resolution-algorithm-in-python/
# FIXME: rework this algorithm to check consistency
def get_task_batches(nodes):

    # Build a map of node names to node instances
    name_to_instance = dict( (n.name, n) for n in nodes )

    # Build a map of node names to dependency names
    name_to_deps = dict( (n.name, n.depends) for n in nodes )

    # This is where we'll store the batches
    batches = []

    # While there are dependencies to solve...
    while name_to_deps:

        # Get all nodes with no dependencies
        ready = {name for name, deps in name_to_deps.items() if not deps}

        # If there aren't any, we have a loop in the graph
        # print("name_to_deps:", name_to_deps)
        if not ready:
            msg  = "Circular dependencies found!\n"
            msg += format_dependencies(name_to_deps)
            raise ValueError(msg)

        # print("ready:", ready)
        # Remove them from the dependency graph
        for name in ready:
            del name_to_deps[name]
        name_to_deps_values = name_to_deps.values()
        # print("name_to_deps_values:", name_to_deps_values)
        for deps in name_to_deps_values:
            deps.difference_update(ready)

        # Add the batch to the list
        batches.append( {name_to_instance[name] for name in ready} )

    # Return the list of batches
    return batches

# Format a dependency graph for printing
def format_dependencies(name_to_deps, type=''):
    msg = []
    # print("name_to_deps: ", name_to_deps)
    for name, deps in name_to_deps.items():
        for parent in deps:
            msg.append("%s -> %s (%s)" % (name, parent, type))
    return "\n".join(msg)

# Create and format a dependency graph for printing
def format_nodes(nodes):
    output = format_dependencies( dict( (n.name, n.dep_networks) for n in nodes ), 'network' ) + '\n'
    output += format_dependencies( dict( (n.name, n.dep_volumes) for n in nodes ), 'volume' ) + '\n'
    output += format_dependencies( dict( (n.name, n.dep_services) for n in nodes ), 'service' ) + '\n'
    return output


def value2str(value, prop, prefix=None):
    output = ''
    prefix = prefix or ('--' + prop + '=')
    if value is not None:
        value = Node.makeAnArray( value )
        for v in value:
            output += prefix + str(v) + ' '
    return output

def prop2str(dict, prop, prefix=None, default=None):
    value = dict.get(prop, default)
    return value2str(value, prop, prefix)

@click.group()
@click.version_option()
def cli():
    pass

def process_yaml(dc_filename):
    dc_yml = yaml.load(open(dc_filename), Loader=yaml.FullLoader)

    volumes = [*dc_yml.get('volumes', [])]
    # print("Volumes found: ", volumes)
    nodes = []

    for volume in volumes:
        volume_impl = dc_yml['volumes'][volume]
        docker_obj = {
            "name": volume,
            "driver": prop2str( volume_impl, 'driver'),
            "labels": prop2str( volume_impl, 'labels'),
            "options": prop2str( volume_impl, 'driver_opts', '-o'),
        }

        nodes.append(Node(docker_obj, 'volume'))

    networks = [*dc_yml.get('networks', [])]
    # print("Networks found: ", networks)

    for network in networks:
        network_impl = dc_yml['networks'][network]
        docker_obj = {
            "name": network,
            "driver": prop2str( network_impl, 'driver'),
            "attachable": prop2str( network_impl, 'attachable'),
            "labels": prop2str( network_impl, 'labels'),
            "options": prop2str( network_impl, 'driver_opts', '-o'),
        }

        nodes.append(Node(docker_obj, 'network'))

    services = [*dc_yml['services']]
    # print("Services found: ", services)

    for service in services:
        svc_impl = dc_yml['services'][service]

        docker_obj = {
            "name": svc_impl.get('container_name', service),
            "command": svc_impl.get('command', ''),
            "image": svc_impl['image'],
            "networks": prop2str( svc_impl, 'networks', '--network='),
            "ports": prop2str( svc_impl, 'ports', '-p '),
            "entrypoint": prop2str( svc_impl, 'entrypoint'),
            "volumes": prop2str( svc_impl, 'volumes', '-v '),
            "env": prop2str( svc_impl, 'environment', '-e '),
            "expose": prop2str( svc_impl, 'expose'),
            "links": prop2str( svc_impl, 'links', '--link='),
            "hostname": prop2str( svc_impl, 'hostname'),
        }

        build_impl = svc_impl.get('build')
        if build_impl is not None:
            docker_obj['build'] = {
                "context": build_impl.get('context', '.'),
                "dockerfile": build_impl.get('dockerfile', 'Dockerfile'),
                "args": prop2str( build_impl, 'args', '--build-arg='),
            }

        node = Node(docker_obj)

        # The following properties must be analyzed separately because they can
        # reference items elsewhere (i.e. volumes, networks or other services...)
        dnsList = svc_impl.get('dns', [])
        if not isinstance(dnsList, list):
            dnsList = [dnsList]
        for index, dns in enumerate(dnsList):
            if not re.match(IPV4ADDR, dns) and not re.match(IPV6ADDR, dns):
                dnsList[index] = "$IP"
                docker_obj["inspect"] = {
                    "variable": 'IP',
                    "what": '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                    "from": dns
                }
                node.addDepService(dns)

        docker_obj["dns"] = value2str( dnsList, 'dns' )

        node.addDepNetwork(svc_impl.get('networks'))
        links = svc_impl.get('links', [])
        if not isinstance( links, list ):
            links = [links]
        for link in links:
            _link = link.split(':')
            if len(_link) > 1:
                node.addDepService(_link[0])

        volumes = svc_impl.get('volumes', [])
        if not isinstance( volumes, list ):
            volumes = [volumes]
        for volume in volumes:
            _volume = volume.split(':')
            if len(_volume) > 1 and re.match(r'[a-zA-Z0-9-_]', _volume[0]):
                node.addDepVolume(_volume[0])

        nodes.append(node)

    # print(format_nodes( nodes ))
    output = defaultdict(list)
    operations = [ "create", "remove", "start", "stop", "build" ]

    batches = get_task_batches( nodes )
    for idx, batch in enumerate(batches):
        for node in batch:
            # print("batch", idx, "- node: ", node.name, "(", node.type, ")")
            for operation in operations:
                currentOutput = Node.output(operation, node) or []
                output[operation+"_"+str(idx)].extend( currentOutput )

    # print(output)
    return len(batches), output, nodes

@cli.command()
@click.option('-f', '--file', 'FILE', default=DEFAULT_FILENAME, show_default=True, help="Docker Compose input file")
@click.option('-o', '--output', 'OUTPUT', default="-", show_default=True, help="Output script name")
def make_shell_script(FILE, OUTPUT):
    ''' Produce shell script from Docker Compose file '''
    batches, output, nodes = process_yaml(FILE)

    template = env.get_template('docker-shell.j2')
    with smart_open(OUTPUT,'w') as fh:
        nodes_name = []
        container_nodes_name = []
        build_nodes = []

        for node in nodes:
            node_name = node.name
            nodes_name.append(node_name)
            if node.type is 'service':
                container_nodes_name.append(node_name)
            if node.build:
                build_nodes.append(node_name)

        print(template.render(
                output=output,
                nodes=nodes,
                nodes_name=nodes_name,
                container_nodes_name=container_nodes_name,
                batches=batches,
                build_nodes=build_nodes
            ),
            file=fh
        )
        fh.flush()

@cli.command()
def show_builtins():
    ''' Show list of builtins (templates, etc) available '''
    print("Templates available: ", env.list_templates())

@cli.command()
@click.option('-f', '--file', 'FILE', default=DEFAULT_FILENAME, show_default=True, help="Docker Compose input file")
def list_services(FILE):
    ''' List services from Docker Compose file '''
    dc_yml = yaml.load(open(FILE), Loader=yaml.FullLoader)
    services = [*dc_yml['services']]
    with smart_open('-','w') as fh:
        for service in services:
            print(service, file=fh)
        fh.flush()
