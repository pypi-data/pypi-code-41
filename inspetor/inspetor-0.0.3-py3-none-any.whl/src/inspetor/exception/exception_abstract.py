import re
import logging


class ExceptionAbstract(Exception):
    status_code = 500
    severity    = logging.INFO

    GENERIC_ERROR = {
        'message': 'Generic Error',
        'code': 0000
    }

    NOT_FOUND = {
        'message': 'Not found',
        'code': 404,
        'http_status': 404
    }

    NOT_CAUGHT = {
        'message': 'Server Internal Error',
        'code': 500,
        'http_status': 500
    }

    def __init__(self, error_info, status_code=None, payload=None, supress=False):
        """Exception Class

        Keyword arguments:
        error_info  -- dict
        status_code -- integer
        payload     -- dict
        """
        Exception.__init__(self)

        self.severity    = error_info.get('severity', self.severity)
        self.message     = error_info.get('message', 'Unknow Error')
        self.code        = error_info.get('code', 0000)
        self.status_code = error_info.get('http_status', self.status_code)
        self.supress     = supress

        if status_code is not None:
            self.status_code = status_code

        self.payload = payload
