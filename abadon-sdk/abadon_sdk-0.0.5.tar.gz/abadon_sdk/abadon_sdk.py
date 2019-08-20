from functools import wraps
import logging
import requests
import json

from abadon_sdk.env import (
    ABADON_LIB_SERVER_HOST,
    ABADON_LIB_SEND_MSG,
    ABADON_LIB_ROUTE_HEADER,
)

logger = logging.getLogger(__name__)

__all__ = [
    "AbadonSDK"
]


class AbadonSDK(object):
    def __init__(self, id):
        self.__server_url = ABADON_LIB_SERVER_HOST + ABADON_LIB_ROUTE_HEADER
        self.__id = id

    def send_info_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, 0)
            func(*args, **kwargs)

        return wrapper

    def send_warning_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, 1)
            func(*args, **kwargs)

        return wrapper

    def send_done_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, 2)
            func(*args, **kwargs)

        return wrapper

    def send_error_decoration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__post_message(args, kwargs, 3)
            func(*args, **kwargs)

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
                "status": 2,
            }), headers=headers)
        except BaseException as e:
            logger.error(str(e))

    def __post_message(self, args, kwargs, status):
        kv_list = ["{k} = {v}".format(k=k, v=v) for k, v in kwargs.items()]
        self.post_message(" ".join(args) + "\n" + " ".join(kv_list), status)
