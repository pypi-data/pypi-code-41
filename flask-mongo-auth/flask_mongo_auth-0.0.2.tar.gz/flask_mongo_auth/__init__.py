import json
from enum import Enum
from functools import wraps
from operator import mul
from typing import Mapping, Any, Dict, Union, Iterable

import flask
import flask_requests
from blinker import Namespace
from flask import abort
from flask import g
from nezha.hash import hash_hmac
from nezha.redis import Redis
from nezha.udict import ImmutableDict
from pymongo import MongoClient
from werkzeug.exceptions import HTTPException

flask_authentication = Namespace()
user_login = flask_authentication.signal('user_login')
got_token = flask_authentication.signal('got_token')


class Accounts(Enum):
    account_name = 'account_name'
    company_uuid = 'company_uuid'
    password = 'password'
    real_name = 'real_name'
    unique_field = 'account_name'


class ProjectConfig(Enum):
    pass


class HTTPCode(Enum):
    # 1、语义有误，当前请求无法被服务器理解。除非进行修改，否则客户端不应该重复提交这个请求。
    # 2、请求参数有误。
    bad_request = 400
    # 未授权
    unauthorized = 401
    # 服务器已经理解请求，但是拒绝执行它
    forbidden = 403
    # 404
    not_found = 404
    # 500
    system_error = 500


class BlockPermission(Enum):
    unique_field = 'unique_field'
    block_name = 'block_name'


def check_condition(condition_index: int):
    def decorate(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            condition = args[condition_index]
            if not set(condition.keys()).issubset(set(map(lambda x: x.value, Accounts))):
                raise ValueError(f'condition {condition} keys not match to Accounts')
            return func(self, *args, **kwargs)

        return wrap

    return decorate


class Authentication:

    def __init__(self,
                 mongo_client: MongoClient,
                 mongo_db: str,
                 cache_obj: Any,
                 collection_account: str = 'accounts',
                 collection_permission: str = 'permission',
                 unique_field: str = 'account_name'):
        """

        :param mongo_client:
        :param mongo_db:
        :param cache_obj:
        :param collection_account:
        :param collection_permission:
        :param unique_field: unique filed in accounts used to join other collections
        """
        self.mongo_client = mongo_client
        self.mongo_db = mongo_db
        self.collection_account = collection_account
        self.collection_permission = collection_permission
        self.cache_obj = cache_obj
        self.unique_field = unique_field

    @check_condition(0)
    def can_login(self, condition: Mapping) -> bool:
        return self.mongo_client[self.mongo_db][self.collection_account].find_one(condition) is not None

    @staticmethod
    def generate_token(condition: Mapping, salt: str = '') -> str:
        return hash_hmac(salt, ''.join(str(v) for k, v in locals().items() if k != 'self'))

    @check_condition(1)
    def cache_token(self, token: str, condition: Mapping):
        self.cache_obj.set(token, condition)

    def get_cache(self, token: str) -> Dict:
        return self.cache_obj.get(token, None)

    def has_permission(self, token: str, block: str) -> bool:
        cache_condition = self.get_cache(token)
        condition = {
            BlockPermission.unique_field.value: cache_condition[self.unique_field],
            BlockPermission.block_name: block
        }
        return self.mongo_client[self.mongo_db][self.collection_account].find_one(condition) is not None


def view_login(authentication: Authentication, where='json') -> str:
    """
    request.mimetype is 'application/json' and data is :
        {
        "username":"xxxx",
        "password": "xxxxx"
        }

    call example:
    >>>from flask import Flask
    >>>app = Flask(__name__)
    >>>from functools import partial
    >>>@app.route('/login', methods=['post'])
    >>>def login():
    >>>     return view_login()
    :return:
    """

    account_name, password = flask_requests.get_data(where, 'username', 'password')
    condition = dict(account_name=account_name, password=password)
    if authentication.can_login(condition):
        token = authentication.generate_token(condition)
        user_login.send(account_name, password=password, token=token)
        return token
    return abort(HTTPCode.forbidden.value)


def cache_user_info_when_first_login(redis_client: Redis, account_name: str,
                                     password: str, token: str, *args, **kwargs) -> None:
    """
    call example:
    >>>from functools import partial
    >>>from flask import Flask
    >>>@user_login.connect
    >>>def user_info(account_name: str, password: str, token: str, *args, **kwargs):
    >>>     return partial(cache_user_info_when_first_login, redis_client='redis client')(password, token, *args, **kwargs)
    :param redis_client:
    :param account_name:
    :param password:
    :param token: cache key is token, value is args.
    :param args:
    :param kwargs:
    :return:
    """
    redis_client.set(token, locals(), mul(3600, 24))


def mount_user_info(token: str, redis_client: Redis) -> None:
    user_info = redis_client.get(token)
    if not user_info:
        return abort(HTTPCode.forbidden.value)
    user_info = json.loads(user_info)
    g.account_name = user_info.get('account_name')
    g.company_uuid = user_info.get('company_uuid')
    g.password = user_info.get('password')
    g.real_name = user_info.get('real_name')


def verify_token(authentication: Authentication) -> Union[str, None]:
    """
    example:

    :param authentication:
    :return:
    """

    def get_token_from_request() -> str:
        try:
            data = flask_requests.get_data('url', 'token')
            if not data:
                raise ValueError(f'get data from {flask.request.full_path} failed')
            return data[0]
        except Exception as e:
            raise ValueError(e)

    try:
        token = get_token_from_request()
    except ValueError as e:
        return abort(HTTPCode.forbidden.value)
    cache = authentication.get_cache(token)
    if not cache:
        return abort(HTTPCode.unauthorized.value)
    got_token.send(token)


def hook_before_request(authentication: Authentication, redis_client: Redis):
    """
    example:
    >>>@app.before_request
    >>>def handle_token():
    >>>     hook_before_request
    :param authentication:
    :param redis_client:
    :return:
    """
    if not (flask.request.path in ('/login',) or flask.request.method == 'OPTIONS'):
        verify_token(authentication)
        mount_user_info(g.token, redis_client)


def hook_error_handler(error):
    if isinstance(error, HTTPException):
        return error
    return abort(500)


def hook_before_first_request(app: flask.Flask, config: Iterable):
    """
    example:
    >>>@app.errorhandler(Exception)
    :param app:
    :param config: {key: 'project config key name', value: 'project config value'}
    :return:
    """
    setattr(app, 'project_config', ImmutableDict(map(lambda x: (x['key'], x['value']), config)))
