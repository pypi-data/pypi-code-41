#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module flask_easylog.util
---------------------------

util for flask_easylog

"""

from logging import DEBUG
from flask import current_app
from flask.helpers import _endpoint_from_view_func
from functools import partial, wraps

try:
    from logging import _levelToName, _nameToLevel
except:
    from logging import _levelNames
    _levelToName = { level : _levelNames[level] for level in _levelNames if isinstance(level, int)  }
    _nameToLevel = { name : _levelNames[name] for name in _levelNames if not isinstance(name, int)  }




class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# create a singleton for python3
# for compatible python2, I use module **six**

import six

@six.add_metaclass(Singleton)
class _SpecificLevelLog(dict):
    def __init__(self):
        dict.__init__(self)
    
    def __getitem__(self, name):
        try:
            return dict.__getitem__(self, name)
        except:
            try:
                return current_app.logger.getEffectiveLevel()
            except:
                raise ValueError('not context current_app')

SpecificLevelLog = _SpecificLevelLog()

def _add_log(level, func, endpoint=None):
    if not isinstance(level, int):
        level = DEBUG
    if not endpoint:
        endpoint = _endpoint_from_view_func(func)
    SpecificLevelLog[endpoint] = level

def log(level=DEBUG, endpoint=None):
    def _decorator(func):
        _add_log(level, func, endpoint)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return _decorator(level) if callable(level) else _decorator
