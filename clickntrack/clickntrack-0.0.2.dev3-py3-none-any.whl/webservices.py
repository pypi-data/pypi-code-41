#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Xavier ROY'

import json
import logging
import sys

import bottle as app
from bottle import request, response
from monkey.dao.core import ObjectNotFoundError, DuplicateKeyError, PersistenceError
from monkey.ioc.core import Registry

from clickntrack.util import JSONEncoder
from clickntrack.services import EntryService

################
# Global vars  #
################

logger = logging.getLogger('clickntrack.webservices')
logger.info('Loading webservices module...')

registry: Registry = {}


################
# RESTFul API  #
################

@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/<:re:.*>', method='OPTIONS')
def options():
    print('OPTIONS')
    return {}


@app.get('/hello')
def hello():
    return {'text': 'Hi Click\'n\'Track !'}


# Redirection API

@app.get('/<short_name>')
def go_to(short_name):
    logger.debug('GET /{}'.format(short_name))
    go_to(short_name, 'default')


@app.get('/<short_name>/<channel>')
def go_to(short_name, channel):
    host = request.urlparts.hostname
    logger.debug('GET /{}/{}'.format(short_name, channel))
    try:
        referer = request.headers['Referer']
    except KeyError:
        referer = ""
    user_agent = request.headers['User-Agent']
    remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR') or request.environ.get('REMOTE_ADDR')
    entry_service = registry.get('entry_service')
    try:
        target = entry_service.get_target_url(host, short_name, channel, referer, user_agent, remote_addr)
        response.status = 302
        response.headers['Location'] = target
        return
    except ObjectNotFoundError:
        response.status = 404
        return


# Back-office API

@app.get('/s/entry')
def find_by_host_and_short_name():
    try:
        host = request.params.getone('host')
        short_name = request.params.getone('shortname')
        logger.debug('GET /s/entry?host={}&shortname={}'.format(host, short_name))
        if (host is None) | (short_name is None):
            raise ValueError
        try:
            entry_service = registry.get('entry_service')
            entry = entry_service.get_one_by_host_and_short_name(host, short_name)
            response.headers['Content-Type'] = 'application/json'
            return _dumps(entry)
        except ObjectNotFoundError:
            response.status = 404
            return
    except ValueError:
        logger.error(sys.exc_info()[0])
        response.status = 400
        return


@app.get('/s/entry/<uid:int>')
def find_by_id(uid):
    logger.debug('GET /s/entry/{}'.format(uid))
    try:
        entry_service = registry.get('entry_service')
        entry = entry_service.get_one_by_id(int(uid))
        response.headers['Content-Type'] = 'application/json'
        return _dumps(entry)
    except ObjectNotFoundError:
        response.status = 404
        return


@app.get('/s/entry/list')
def list_all():
    try:
        skip = int(request.params['skip'])
    except KeyError:
        skip = 0
    try:
        limit = int(request.params['limit'])
    except KeyError:
        limit = 10
    try:
        sort_key = request.params['sortKey']
    except KeyError:
        sort_key = '_id'
    try:
        sort_dir = int(request.params['sortDir'])
    except KeyError:
        sort_dir = 1
    logger.debug('GET /s/entry/list?skip={}&limit={}'.format(skip, limit))
    entry_service = registry.get('entry_service')
    entries: EntryService = entry_service.list(skip, limit, sort_key, sort_dir)
    response.headers['Content-Type'] = 'application/json'
    return '{"entries":' + _dumps(entries) + '}'


@app.get('/s/entry/count')
def count():
    entry_service = registry.get('entry_service')
    c = entry_service.count_all()
    response.headers['Content-Type'] = 'application/json'
    return '{"count": %s}' % c


@app.post('/s/entry')
def create():
    try:
        data = request.json
        print('POST /s/entry data={}'.format(data))
        host = data['host']
        short_name = data['shortName']
        target = data['target']

        entry_service = registry.get('entry_service')
        inserted_id = entry_service.create(host, short_name, target)

        logger.debug('SUCCESS - Created new URL entry with _id: {}'.format(inserted_id))
        response.status = 201
    except DuplicateKeyError:
        logger.error(sys.exc_info()[0])
        response.status = 409
    except PersistenceError:
        logger.error(sys.exc_info()[0])
        response.status = 502
    except ValueError:
        logger.error(sys.exc_info()[0])
        response.status = 400
    return


@app.put('/s/entry')
def update():
    # NOT YET IMPLEMENTED
    response.status = 501
    return


@app.delete('/s/entry/<uid:int>')
def delete(uid):
    logger.debug('DELETE /s/entry/{}'.format(uid))
    try:
        entry_service = registry.get('entry_service')
        deleted_count = entry_service.delete_one_by_id(int(uid))
        logger.debug('SUCCESS - {} URL entries deleted'.format(deleted_count))
    except PersistenceError:
        logger.error(sys.exc_info()[0])
        response.status = 502
    return


def _dumps(obj):
    return json.dumps(obj, cls=JSONEncoder)


################
# Launcher     #
################

def start(reg, hostname, port):
    logger.info('webservices.start(registry, hostname, port)')
    global registry
    registry = reg
    app.run(host=hostname, port=port, debug=False, reloader=False)
