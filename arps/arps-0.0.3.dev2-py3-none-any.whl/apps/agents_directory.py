import sys
import logging
import logging.handlers
import argparse

from aiohttp import web
import simplejson as json

from arps import __version__ as arps_version
from arps.core import logger_setup
from arps.apps.run_server import run_server, RoutesBuilder

# pylint: disable-msg=C0103
logger = logging.getLogger('AgentsDirectory')

agents = {}

def format_result(message, success=True):
    result = 'success' if success else 'failure'
    return json.dumps({'result':result, 'message':message}, indent=4, sort_keys=True)

async def index(_):
    logger.info('index requested')
    return web.Response(text=format_result({'available commands': {'add':'/add?id=XX&address=XX&port=XX',
                                                                   'get':'/get?id=XX',
                                                                   'remove':'/remove?id=XX',
                                                                   'list':'/list'}}))

async def about(_):
    logger.info('about requested')
    return web.Response(text=format_result(f'agent service directory version {arps_version}'))

async def add(request):
    query = request.rel_url.query

    identifier = query.get('id', None)
    address = query.get('address', None)
    port = query.get('port', None)

    logger.info('add requested')

    if identifier is None or address is None or port is None:
        message = format_result('Missing id, address, or port parameter', success=False)
        logger.info(message)
        return web.Response(text=message)

    if identifier in agents:
        message = format_result('agent {} already added'.format(identifier), success=False)
        logger.info(message)
        return web.Response(text=message)

    agents[identifier] = {'address':address, 'port':port}
    message = format_result('agent {} added'.format(identifier))
    logger.info(message)
    logger.info(agents[identifier])
    return web.Response(text=message)

async def get(request):
    query = request.rel_url.query

    identifier = query.get('id', None)

    logger.info('get requested')

    if identifier is None:
        message = format_result('Missing id parameter', success=False)
        logger.info(message)
        return web.Response(text=message)

    if identifier not in agents:
        message = format_result('agent {} not registered'.format(identifier), success=False)
        logger.info(message)
        return web.Response(text=message)

    message = format_result(agents[identifier])
    logger.info(message)
    return web.Response(text=message)

async def remove(request):
    query = request.rel_url.query

    identifier = query.get('id', None)

    logger.info('remove requested')
    if identifier is None:
        message = format_result('Missing id parameter', success=False)
        logger.info(message)
        return web.Response(text=message)

    if identifier not in agents:
        message = format_result('agent {} not registered'.format(identifier), success=False)
        logger.info(message)
        return web.Response(text=message)

    del agents[identifier]
    message = format_result('agent {} removed'.format(identifier))
    logger.info(message)
    return web.Response(text=message)

async def list_agents(_):
    logger.info('list agents')
    message = format_result(agents)
    logger.info(message)
    return web.Response(text=message, headers={'Access-Control-Allow-Origin':'*'})

def parse_arguments():
    parser = argparse.ArgumentParser('Runs agent directory service.')
    parser.add_argument('--port', type=int, default=1500, help='port to listen')

    return parser.parse_args(sys.argv[1:])

def main():
    parsed_args = parse_arguments()

    logger_setup.set_to_rotate(logger, file_name_prefix='agents_directory')

    get_routes = {r'/' : index,
                  r'/add' : add,
                  r'/get' : get,
                  r'/remove' : remove,
                  r'/list' : list_agents,
                  r'/about' : about}

    routes_builder = RoutesBuilder()
    routes_builder.add_get(get_routes)

    try:
        run_server(parsed_args.port, routes_builder.routes)
        logger.info('rest service has stopped')
        sys.exit(0)
    except RuntimeError as err:
        logger.info(str(err))
        sys.exit(str(err))

if __name__ == '__main__':
    main()
