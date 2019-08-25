#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module flask_easylog.plugin
---------------------------

plugin for flask_easylog

"""
from uuid import uuid4
from logging import Filter, Formatter, Logger, getLogger, DEBUG, CRITICAL, INFO, NOTSET, FileHandler, StreamHandler
from time import time, gmtime, asctime, strftime, localtime

from flask import current_app, request, Flask
from flask.logging import default_handler

from .util import SpecificLevelLog

FMT_ACCESS_LOG = '%(remoteAddr)s - %(user)s [%(timeRequestReceived)s] "%(method)s %(path)s %(serverProtocol)s" %(statusCode)s %(message)s'
FMT_ACCESS_LOG_SEC = FMT_ACCESS_LOG + '%(timestamp).3f second(s)'

_monthname = [None,
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

class KeyFilter(Filter):
    """
    Generic class for add keys in record
    """
    def _load_keys(self, record, keys):
        for name, value in [(i,keys[i]) for i in keys]:
            setattr(record, name, value)
        return True

def key_request_id():
    """
    Return a dict with a key: 
    
    -requestId with value X-Request-ID of request
    """
    try:
        res = {'requestId' : request.environ.get('X-Request-ID', '-')}
    except:
        res = {'requestId' : ''}
    return res

class RequestIdFilter(KeyFilter):
    """
    This is a filter which injects request Id information into the log.
    """

    def filter(self, record):
        self._load_keys(record, key_request_id())
        return True

def keys_request():
    """
    Return a dict with key

    - secretKey from app config
    - serverName from app config
    - serverPort from app config
    - cookieName from app config
    - cookieDomain from app config
    - cookiePath from app config
    - args from request
    - path from request
    - method from request
    - remoteAddr from request
    - url from request
    - user from request
    - rule from request
    - endpoint from request
    - scheme from request
    - fullPath from request
    - httpHost from request
    - queryString from request
    - requestUri from request
    - serverProtocol from request
    """
    try:
        res = {
            'secretKey' : current_app.config.get('SECRET_KEY',''),
            'serverName' : current_app.config.get('SERVER_NAME',''),
            'serverPort' : current_app.config.get('SERVER_PORT',''),
            'cookieName' : current_app.config.get('SESSION_COOKIE_NAME',''),
            'cookieDomain' : current_app.config.get('SESSION_COOKIE_DOMAIN',''),
            'cookiePath' : current_app.config.get('SESSION_COOKIE_PATH',''),
            'args' : ','.join(["%s:%s" % (arg, request.args[arg]) for arg in request.args]),
            'path' : request.path,
            'method' : request.method,
            'remoteAddr' : request.remote_addr,
            'url' : request.url,
            'user' : getattr(request, 'user','-'),
            'rule' : getattr(request.url_rule, 'rule',''),
            'endpoint' : getattr(request, 'endpoint',''),
            'scheme' : request.scheme,
            'fullPath' : request.full_path,
            'pathInfo' : request.environ.get('PATH_INFO',''),
            'httpHost' : request.environ.get('HTTP_HOST',''),
            'queryString' : request.environ.get('QUERY_STRING',''),
            'requestUri' : request.environ.get('REQUEST_URI',''),
            'serverProtocol' : request.environ.get('SERVER_PROTOCOL',''),
        }
    except:
        res  = {
            'secretKey' : '',
            'serverName' : '',
            'serverPort' : '',
            'cookieName' : '',
            'cookieDomain' : '',
            'cookiePath' : '',
            'args' : '',
            'path' : '',
            'method' : '',
            'remoteAddr' : '',
            'url' : '',
            'user' : '',
            'rule' : '',
            'endpoint' : '',
            'scheme' : '',
            'fullPath' : '',
            'pathInfo' : '',
            'httpHost' : '',
            'queryString' : '',
            'requestUri' : '',
            'serverProtocol' : '',
        }
    return res

class RequestFilter(KeyFilter):
    """
    This is a filter which injects request information into the log.
    """

    def filter(self, record):
        self._load_keys(record, keys_request())
        return True

def keys_timestamp():
    """
    Return a dict with a key: 
    
    - timestamp
    - timeRequestReceived
    - contentLength from response
    - statusCode from response
    - status from response
    """
    try:
        res = {
            'timestamp' : not getattr(request, '_timestamp_stop', None) and -1 or request._timestamp_stop - request._timestamp_start ,
            'timeRequestReceived' : request._time_received, 
            'contentLength' : request._response.get('Content-Length',''),
            'statusCode' : request._response.get('status_code',' '*3),
            'status' : request._response.get('status','')
        }
    except:
        year, month, day, hh, mm, ss = localtime(time())[:6]
        res = {
            'timestamp' : -1 ,
            'timeRequestReceived' : "%02d/%3s/%04d %02d:%02d:%02d" % (day, _monthname[month], year, hh, mm, ss), 
            'contentLength' : '',
            'statusCode' : ' ',
            'status' : ''
        }
    return res

class RequestTimeStampFilter(KeyFilter):
    """
    This is a filter which injects request information into the log.
    """

    def filter(self, record):
        self._load_keys(record, keys_timestamp())
        return True

class EasyLog(object):
    """
    This is a extension for flask application
    Add information in log
    Parameters

    - app: flask application
    - fmt: format de log for your flask application
    - werkzeug: enabled or disabled the werkzeug logger (default False)
    - afterlog: enabled or disabled sending a message at the end of response (default False)
    - aftermsg: if accesslog, format of message sending (default 'END')
    - afterlevel: if accesslog, level of message sending (default INFO)
    - beforelog: enabled or disabled sending a message at the end of response (default False)
    - beforemsg: if accesslog, format of message sending (default 'START')
    - beforelevel: if accesslog, level of message sending (default INFO)
    - fmtaccesslog: format for logger "access.log" (default FMT_ACCESS_LOG)
    - enabledaccesslog: add FileHandler if "FLASK_ENV" is production and path value not null (default None)
    """
    def __init__(self, 
            app = None, 
            fmt = None, 
            werkzeug = False,
            afterlog = False,
            aftermsg = 'END',
            afterlevel = INFO,
            beforelog = False,
            beforemsg = 'START',
            beforelevel = INFO,
            fmtaccesslog = FMT_ACCESS_LOG,
            enabledaccesslog = None):
        self._afterLog = afterlog
        self._afterMsg = aftermsg
        self._afterLevel = afterlevel
        self._beforeLog = beforelog
        self._beforeMsg = beforemsg
        self._beforeLevel = beforelevel
        if app is not None:
            self.init_app(app)
        if fmt is not None:
            default_handler.setFormatter(Formatter(fmt))
        if not werkzeug:
            getLogger('werkzeug').setLevel(100)
        getLogger('access.log')
        if enabledaccesslog and app.env == 'production':
            fileH = FileHandler(enabledaccesslog)
            fileH.setLevel(INFO)
            formatter = Formatter(fmtaccesslog)
            fileH.setFormatter(formatter)
            getLogger('access.log').addHandler(fileH)
        self._add_specific_log()

    def init_app(self, app):
        self.app = app
        self._add_extension_request_id()
        self._add_extension_request()
        self._add_extension_timestamp()
        self.app.logger._log = self._log()
    
    def _add_filter(self, fi):
        self.app.logger.addFilter(fi)
        getLogger('access.log').addFilter(fi)
    
    def _add_extension_request_id(self):
        self._add_filter(RequestIdFilter())
        self.app.before_request(self.add_request_id)
    
    def _add_extension_request(self):
        self._add_filter(RequestFilter())
    
    def _add_extension_timestamp(self):
        self.app.run = self._run()
        self.app.before_request(self.start_timestamp())
        self._add_filter(RequestTimeStampFilter())

    @staticmethod
    def add_request_id():
        if not request.environ.get('X-Request-ID', None):
            request.environ['X-Request-ID'] = str(uuid4()).replace('-','')

    def _log(self):
        """
        Add arguments in your message of log
        """
        def _log(level, msg, args, **kwargs):
            new_args = keys_request()
            new_args.update(key_request_id())
            new_args.update(keys_timestamp())
            msg = msg % new_args
            Logger._log(self.app.logger, level, msg, args, **kwargs)
        return _log

    def _run(self):
        """
        Add start/stop _timestamp before run
        """
        def run(**kwargs):
            self.app.after_request(self.stop_timestamp())
            Flask.run(self.app, **kwargs)
        return run

    def start_timestamp(self):
        def start_timestamp():
            request._timestamp_start = time()
            request._timestamp_stop = None
            year, month, day, hh, mm, ss = localtime(request._timestamp_start)[:6]
            request._time_received = "%02d/%3s/%04d %02d:%02d:%02d" % (
                    day, _monthname[month], year, hh, mm, ss)
            request._response = {}
            if self._beforeLog:
                self.app.logger.log(self._beforeLevel, self._beforeMsg)
        return start_timestamp

    def stop_timestamp(self):
        def stop_timestamp(response):
            request._timestamp_stop = time()
            request._response['Content-Length'] = response.headers.get("Content-Length",'')
            request._response['status_code'] = response.status_code
            request._response['status'] = response.status
            if len(getLogger('access.log').handlers):
                getLogger('access.log').warning('')
            if self._afterLog:
                self.app.logger.log(self._afterLevel, self._afterMsg)
            return response
        return stop_timestamp

    def _add_specific_log(self):
        self.app.logger.isEnabledFor = self._specific_isEnabledFor()
 
    def _specific_isEnabledFor(self):
        def isEnabledFor(level):
            try:
                if level >= SpecificLevelLog[request.endpoint]:
                    return True
                return False
            except:
                return Logger.isEnabledFor(self.app.logger, level)  
        return isEnabledFor
 