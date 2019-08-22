import sys
from functools import wraps
import logging
import requests
import json
from enum import Enum

if sys.version_info >= (3,):
    from abadon_sdk.env import (
        ABADON_LIB_SERVER_HOST,
        ABADON_LIB_SEND_MSG,
        ABADON_LIB_ROUTE_HEADER,
    )
else:
    from env import (
        ABADON_LIB_SERVER_HOST,
        ABADON_LIB_SEND_MSG,
        ABADON_LIB_ROUTE_HEADER,
    )
logging.basicConfig()
logger = logging.getLogger(__name__)

__all__ = [
    "AbadonSDK",
    "Status"
]


class Status(Enum):
    Info = 0
    Warning = 1
    Done = 2
    Error = 3


class AbadonSDK(object):
    def __init__(self, id):
        self.__server_url = ABADON_LIB_SERVER_HOST + ABADON_LIB_ROUTE_HEADER
        self.__id = id

    def send_info_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, Status.Info.value)
            return func(*args, **kwargs)

        return wrapper

    def send_warning_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, Status.Warning.value)
            return func(*args, **kwargs)

        return wrapper

    def send_done_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, Status.Done.value)
            return func(*args, **kwargs)

        return wrapper

    def send_error_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, Status.Error.value)
            return func(*args, **kwargs)

        return wrapper

    def post_message(self, content, status):
        try:
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            requests.post(url=self.__server_url + ABADON_LIB_SEND_MSG, data=json.dumps({
                'id': self.__id,
                "content": content,
                "status": status,
            }), headers=headers)
        except BaseException as e:
            logger.error(str(e))

    def post_done_message(self):
        try:
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            requests.post(url=self.__server_url + ABADON_LIB_SEND_MSG, data=json.dumps({
                'id': self.__id,
                "content": 'finish',
                "status": Status.Done.value,
            }), headers=headers)
        except BaseException as e:
            logger.error(str(e))

    def __post_message(self, args, kwargs, status):
        kv_list = ["{k} = {v}".format(k=k, v=v) for k, v in kwargs.items()]
        self.post_message(" ".join(args) + "\n" + " ".join(kv_list), status)
