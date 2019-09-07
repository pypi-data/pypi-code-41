import logging
import sys

import click

from symmetry.api import NodeInfo, RoutingRecord
from symmetry.webapp.client import ApiClient, NoSuchNodeException, NoSuchServiceException

client: ApiClient


@click.group()
@click.option('--debug/--no-debug', default=False)
def symmetry(debug):
    if debug:
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))
        logging.basicConfig(level=logging.DEBUG)


@symmetry.command()  # @cli, not @click!
def list_nodes():
    nodes = client.get_nodes()
    for node in nodes:
        user = node.user + '@' if node.user else ''
        click.echo(f'{node.node_id}: {user}{node.host}:{node.ssh_port} {node.mac}')


@symmetry.command()
@click.option('--node-id', required=True, help='The id of the node')
@click.option('--host', required=True, help='The hostname of the node')
@click.option('--user', required=False, help='The username to access the node')
@click.option('--ssh-port', required=False, help='The ssh port to access the node')
@click.option('--mac', required=False, help='The mac address of the node')
def add_node(node_id, host, user=None, ssh_port=None, mac=None):
    node = NodeInfo(node_id, host, mac=mac, user=user, ssh_port=ssh_port)
    client.add_node(node)


@symmetry.command()
@click.option('--node-id', required=True, help='The id of the node')
def remove_node(node_id):
    try:
        deleted = client.remove_node(node_id)
    except NoSuchNodeException:
        click.echo(f'node {node_id} does not exist')
        sys.exit(1)

    if deleted:
        click.echo(f'node {node_id} deleted')
    else:
        click.echo(f'could not delete node {node_id}')
        sys.exit(1)


@symmetry.command()
@click.option('--service', '-s', required=False, help='The service to print routes for')
def list_routes(service=None):
    def print_record(record):
        click.echo('Record for %s' % record.service)
        click.echo('weight   target')
        for j in range(len(record.hosts)):
            click.echo('%-8s %s' % (record.weights[j], record.hosts[j]))

    if not service:
        routes = client.get_routes()
        for i in range(len(routes)):
            route = routes[i]
            print_record(route)
            if i < (len(routes) - 1):
                click.echo('')
    else:
        try:
            route = client.get_route(service)
            print_record(route)
        except NoSuchServiceException:
            click.echo(f'No such service {service}')


@symmetry.command()
@click.option('--service', '-s', required=True, help='The service of which to remove the routes')
def remove_route(service):
    try:
        record = client.get_route(service)
    except NoSuchServiceException:
        click.echo(f'No record for service {service}')
        sys.exit(0)

    if client.remove_route(service):
        click.echo(f'Removed {record}')
    else:
        click.echo(f'Could not remove records for {service}')


@symmetry.command()
@click.option('--service', '-s', required=True, help='The service to create the route for')
@click.option('--route', '-r', required=True, help='The route in the form of <host> <weight>', multiple='True',
              type=click.Tuple([str, float]))
def set_route(service, route):
    hosts = [r[0] for r in route]
    weights = [r[1] for r in route]

    record = RoutingRecord(service, hosts, weights)
    client.set_route(record)


def main(*args, **kwargs):
    global client
    client = ApiClient()
    symmetry(*args, **kwargs)


if __name__ == '__main__':
    main()
