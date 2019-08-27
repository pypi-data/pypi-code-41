#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import logging
from multiprocessing import Process, Queue
from pleio_profile_sync_client.client import Client
from pleio_profile_sync_client.mapper import Mapper
from pleio_profile_sync_client.worker import Worker
from pleio_profile_sync_client.log_handler import HTTPLogHandler
from urllib.parse import urlparse

NUMBER_OF_WORKERS = 3

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
def validate_secret(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter API secret is not defined')
    return str(value)


# pylint: disable=unused-argument
def validate_source(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter source is not defined')
    return value


# pylint: disable=unused-argument
def validate_destination(ctx, param, value):
    if not value:
        raise click.BadParameter('The parameter destination is not defined')

    url = urlparse(value)
    if url.scheme != 'https':
        if url.hostname not in ['127.0.0.1', 'localhost']:
            raise click.BadParameter('The destination is insecure. Destination should be https.')

    return value


@click.command()
@click.option('--api-secret', help='The profile sync API secret. [envvar=API_SECRET]', envvar='API_SECRET',
              callback=validate_secret)
@click.option('--source', help='The source file (formatted as CSV).', type=click.STRING, callback=validate_source)
@click.option('--destination', help='The Pleio subsite providing the profile sync.', callback=validate_destination)
@click.option('--ban', help='Ban users on the site who are not listed in the CSV file. [default=False]',
              type=click.BOOL, default=False)
@click.option('--dry-run', help='Perform a dry run. [default=False]', type=click.BOOL, default=False)
@click.option('--verbose', help='Show verbose output [default=True]', type=click.BOOL, default=False)
def main(api_secret, source, destination, ban, dry_run, verbose): # pylint: disable=too-many-arguments,too-many-locals
    queue = Queue()

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    rest_destination = Client(base_url=destination, api_secret=api_secret, read_only=dry_run)

    http_handler = HTTPLogHandler(client=rest_destination)
    http_handler.setLevel(logging.INFO)
    logger.addHandler(http_handler)

    logger.info('Retrieving and mapping source and destination users')

    mapper = Mapper(source, rest_destination)
    mapper.initialize()

    counts = mapper.count()

    if counts['source'] < 1:
        logger.error('The source file contains no users')
        return

    logger.info('Syncing %s source users and %s destination users', counts['source'], counts['destination'])

    for user in mapper.users_to_update():
        queue.put(('UPDATE', user))

    if ban:
        for user in mapper.users_to_ban():
            queue.put(('BAN', user))

    for _ in range(NUMBER_OF_WORKERS):
        queue.put(('STOP', None))

    for _ in range(NUMBER_OF_WORKERS):
        rest_destination = Client(base_url=destination, api_secret=api_secret, read_only=dry_run)
        worker = Worker(queue, source, rest_destination)
        process = Process(target=worker.run)
        process.daemon = True
        process.start()

    for _ in range(NUMBER_OF_WORKERS):
        process.join()

    logger.info('Finished syncing')


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
