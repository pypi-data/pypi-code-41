#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module flask_easylog.api
---------------------------

api for flask_easylog: change specificLevelLog by endpoint

"""
import json
from logging import DEBUG 
from flask import Blueprint, current_app, request
from .util import SpecificLevelLog
from .util import _levelToName, _nameToLevel

def to_json(fn):
    def _request_fn(*args, **kw):
        try:
            fn_exec = fn(*args, **kw)
            return json.dumps(fn_exec, sort_keys=True, indent=4, separators=(',', ': '))
        except Error as e:
            return e.to_problem()
        else:
            return Error(status=500, title='Error System', type='UNKNOW', detail=e.__str__()).to_problem()   
    return _request_fn


class Error(Exception):
    
    def __init__(self, status=400, title=None, type=None,
                      instance=None, headers=None, detail=None):
        Exception.__init__(self)
        self.status = status
        self.type = type
        self.title = title
        self.instance = instance
        self.detail = detail
        self.headers = headers

    def __str__(self):
        return self.detail

    def to_problem(self):
        current_app.logger.error("{url} {type} {error}".format(url=request.url, 
                                                        type=self.type,
                                                        error=self.__str__()))
        problem_response = {'type': self.type, 
                            'title': self.title, 
                            'detail': self.detail, 
                            'status': self.status,
                            'instance': self.instance }
        body = [json.dumps(problem_response, indent=2), '\n']
        response = current_app.response_class(body, mimetype='application/problem+json',
                                                                 status=self.status)  # type: flask.Response
        if self.headers:
            response.headers.extend(self.headers)
        return response


@to_json
def get_log(endpoint):
    """
    Find specific log level by endpoint
    Returns a endpoint
    :param endpoint: endpoint that needs to be fetched
    :type endpoint: str

    :rtype: dict
    """
    return {'endpoint' : endpoint, 'level' : _levelToName[SpecificLevelLog[endpoint]]}

@to_json
def rm_log(endpoint):
    """
    Delete specific log level by endpoint
    Returns a endpoint
    :param endpoint: endpoint that needs to be fetched
    :type endpoint: str

    :rtype: dict
    """
    if endpoint in SpecificLevelLog.keys():
        del SpecificLevelLog[endpoint]
    return {'endpoint': endpoint, 'level' : _levelToName[SpecificLevelLog[endpoint]]}


@to_json
def get_logs():
    """
    list of endpoint and specific level
    Returns list of endpoint

    :rtype: List[Endpoint]
    """
    return [ {'endpoint' : endpoint, 'level': _levelToName[SpecificLevelLog[endpoint]]} for endpoint in SpecificLevelLog]


@to_json
def set_log(endpoint):
    """
    Updates a specific level log for a endpoint with form data
    update endpoint
    :param endpoint: endpoint that needs to be updated
    :type endpoint: str
    :param body: endpoint object that needs to be updated
    :type body: dict | bytes

    :rtype: None
    """
    try:
        data = json.loads(request.data.decode())
    except:
        raise Error(status=405, title='invalid INPUT', type='RG-002', detail='not dict data')
    if not isinstance(data, dict):
        raise Error(status=405, title='invalid INPUT', type='RG-002', detail='not dict data')
    if not isinstance(data, dict) or endpoint != data.get('endpoint','') or 'level' not in data.keys():
        raise Error(status=405, title='invalid INPUT', type='RG-001', detail='endpoint is not compatible with endpoint object')
    SpecificLevelLog[data['endpoint']] = _nameToLevel.get(data['level'], DEBUG) 
    return {'endpoint' : endpoint, 'level': _levelToName[SpecificLevelLog[endpoint]]}


class Api(Blueprint):

    def __init__(self, name='apilog', import_name=__name__, url_prefix="", *args, **kwargs):
        Blueprint.__init__(self, name, import_name, url_prefix=url_prefix, *args, **kwargs)
        self.add_url_rule('/logs', 'get_logs', get_logs, methods=['GET'])
        self.add_url_rule('/log/<endpoint>', 'get_log', get_log, methods=['GET'])
        self.add_url_rule('/log/<endpoint>', 'set_log', set_log, methods=['PUT'])
        self.add_url_rule('/log/<endpoint>', 'rm_log', rm_log, methods=['DELETE'])
 