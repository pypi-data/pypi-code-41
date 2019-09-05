import re
import socket
import traceback
from threading import Thread

import requests
from flask import request
from werkzeug.exceptions import HTTPException

from .exceptions import ES54Exception

IGNORE_HTTP_CODE = (301, 302, 307, 308, 403, 404)


class ControlHandler:
    def __init__(self, app=None):
        if app is None:
            assert ES54Exception('Not app in args')

        self.app = app
        self.ignore_http_code = self.app.config.get('IGNORE_HTTP_CODE', IGNORE_HTTP_CODE)
        self.send_exception_to_control = self.app.config.get('SEND_EXCEPTION_TO_CONTROL', False)
        self.control_exception_url = self.app.config['CONTROL_EXCEPTION_URL']
        self.service_name = self.app.config.get('SERVICE_NAME')
        self.reg = r"<class '([\w\.\d]*)'>"

        app.register_error_handler(Exception, self.control_handler)

    @staticmethod
    def send_exception(url, json_data):
        try:
            res = requests.post(url, json=json_data, verify=False)
        except Exception as err:
            print(f'Error with send exception to server:\n{err}')
        else:
            if res.status_code != 200:
                print(f'Error with send exception to API:\n{res.text}')

    def control_handler(self, err):
        ext_data = None
        traceb = str(traceback.format_exc())
        message = str(err)
        type_err = str(type(err))
        code = 500
        url = self.control_exception_url

        if self.send_exception_to_control:
            # Parse exception name
            match = re.search(self.reg, type_err)

            if match:
                type_err = match.group(1)

            if isinstance(err, HTTPException):
                code = err.code

            if code not in self.ignore_http_code:
                # Ignore http error

                # Get external data from custom exception
                if isinstance(err, ES54Exception):
                    ext_data = err.get_ext_data()

                json_data = {'type': type_err,
                             'message': message,
                             'traceback': traceb,
                             'ext_data': ext_data,
                             'service_name': self.service_name,
                             'hostname': socket.gethostname(),
                             'full_path': request.full_path,
                             'headers': dict(request.headers),
                             'user_agent': request.user_agent.string,
                             'remote_addr': request.remote_addr,
                             'method': request.method,
                             'scheme': request.scheme,
                             'url': request.url}

                # Run sending data in background so as not to block the main thread
                Thread(target=self.send_exception, args=(url, json_data)).start()

        raise err
