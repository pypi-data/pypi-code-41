import os
import platform
import re
import socket
import sys
import traceback
from threading import Thread

try:
    import ujson as json
except ModuleNotFoundError:
    import json

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

    @staticmethod
    def get_os_data():
        return {'platform': sys.platform,
                'name': os.name,
                'uname': platform.uname()}

    @staticmethod
    def get_python():
        result = {'version': sys.version,
                  'executable': sys.executable,
                  'pythonpath': sys.path,
                  'version_info': {'major': sys.version_info.major,
                                   'minor': sys.version_info.minor,
                                   'micro': sys.version_info.micro,
                                   'releaselevel': sys.version_info.releaselevel,
                                   'serial': sys.version_info.serial}}
        try:
            import pip
            packages = dict([(p.project_name, p.version) for p in pip.get_installed_distributions()])
            result['packages'] = packages
        except Exception:
            pass

        return result

    @staticmethod
    def get_login():
        if os.name == "posix":
            import pwd
            username = pwd.getpwuid(os.geteuid()).pw_name
        else:
            username = os.environ.get('USER', os.environ.get('USERNAME', 'UNKNOWN'))
            if username == 'UNKNOWN' and hasattr(os, 'getlogin'):
                username = os.getlogin()
        return username

    def get_process(self):
        return {'argv': sys.argv,
                'cwd': os.getcwd(),
                'user': self.get_login(),
                'pid': os.getpid(),
                'environ': self.safe_dump(os.environ)}

    @staticmethod
    def safe_dump(dictionary):
        result = {}
        for key in dictionary.keys():
            if 'key' in key.lower() or 'token' in key.lower() or 'pass' in key.lower():
                # Try to avoid listing passwords and access tokens or keys in the output
                result[key] = "********"
            else:
                try:
                    json.dumps(dictionary[key], default=str)
                    result[key] = dictionary[key]
                except TypeError:
                    pass
        return result

    @staticmethod
    def get_headers():
        return dict(request.headers)

    def get_type_err(self, err):
        err_str = str(type(err))
        match = re.search(self.reg, err_str)

        if match:
            err_str = match.group(1)

        return err_str

    def control_handler(self, err):
        ext_data = None
        traceb = str(traceback.format_exc())
        message = str(err)
        type_err = self.get_type_err(err)
        code = 500
        url = self.control_exception_url

        if self.send_exception_to_control:

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
                             'headers': self.get_headers(),
                             'user_agent': request.user_agent.string,
                             'remote_addr': request.remote_addr,
                             'method': request.method,
                             'scheme': request.scheme,
                             'url': request.url,
                             'os': self.get_os_data(),
                             'python': self.get_python(),
                             'process': self.get_process()
                             }

                # Run sending data in background so as not to block the main thread
                Thread(target=self.send_exception, args=(url, json_data)).start()

                raise err

        return err
