# coding: utf-8
#  连接
import datetime
import threading

from dophon_logger import *
from pymongo import MongoClient
from pymongo.database import Database

from dophon_db import properties

logger = get_logger(COMMAND)

"""
连接池
author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())

single_pool = None  # 单例模式获取连接池
cluster_pool = None  # 单例模式获取连接池

pool_action_log = {}

lock = threading.Lock()  # 全局线程锁

def record_support(f):
    def inner_method(*args, **kwargs):
        result = f(*args, **kwargs)
        obj_id = id(result)
        pool_action_log[obj_id] = datetime.datetime.now().timestamp()
        return result

    return inner_method


def record_return(f):
    def inner_method(*args, **kwargs):
        obj_id = id(args[1])
        if hasattr(properties, 'db_pool_exe_time') and getattr(properties, 'db_pool_exe_time'):
            logger.info(
                '用时:' + (datetime.datetime.now().timestamp() - pool_action_log[obj_id]) + '毫秒'
            )
        f(*args, **kwargs)

    return inner_method


def get_pool(conn_kwargs: dict = {}):
    return get_single_pool(conn_kwargs)


def get_single_pool(conn_kwargs: dict = {}):
    global single_pool
    if single_pool:
        # 已存在初始化完毕的单库
        return single_pool
    pool = Pool()
    single_pool = pool.init_pool(properties.pool_conn_num, conn_kwargs=conn_kwargs)
    return single_pool


class Pool(MongoClient):
    _size = 0
    cache_conn_kwargs = {}

    _host = properties.mgdc_host
    _user = properties.mgdc_user
    _password = properties.mgdc_password
    _database = properties.mgdc_database
    _port = properties.mgdc_port
    _charset = 'utf8'

    # 初始化连接池
    def init_pool(self, connect_num: int, conn_kwargs: dict = {}):
        __host = conn_kwargs['host'] if 'host' in conn_kwargs else (
            conn_kwargs['__host'] if '__host' in conn_kwargs else self._host)
        __port = conn_kwargs['port'] if 'port' in conn_kwargs else (
            conn_kwargs['__port'] if '__port' in conn_kwargs else self._port)
        __user = conn_kwargs['user'] if 'user' in conn_kwargs else (
            conn_kwargs['__user'] if '__user' in conn_kwargs else self._user)
        __password = conn_kwargs['password'] if 'password' in conn_kwargs else (
            conn_kwargs['__password'] if '__password' in conn_kwargs else self._password)
        __database = conn_kwargs['database'] if 'database' in conn_kwargs else (
            conn_kwargs['__database'] if '__database' in conn_kwargs else self._database)
        __charset = conn_kwargs['charset'] if 'charset' in conn_kwargs else (
            conn_kwargs['__charset'] if '__charset' in conn_kwargs else self._charset)
        super(Pool, self).__init__(
            host=__host,
            port=__port,
            username=__user,
            password=__password,
            # database=__database,
            # charset=__charset,
            connect=False,
            minPoolSize=1,
            maxPoolSize=connect_num,
        )
        return self.get_conn(__database)

    def __init__(self):
        logger.info(f'初始化连接池 => ({id(self)})')

    # 定义取出连接
    @record_support
    def get_conn(self, database) -> Database:
        # 获取当前配置的数据库链接
        self.__current_connect = self.__current_connect if hasattr(self, '__current_connect') else eval(
            f'self.{database}')
        return self.__current_connect
