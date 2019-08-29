#
#                __   _,--="=--,_   __
#               /  \."    .-.    "./  \
#              /  ,/  _   : :   _  \/` \
#              \  `| /o\  :_:  /o\ |\__/
#               `-'| :="~` _ `~"=: |
#                  \`     (_)     `/
#           .-"-.   \      |      /   .-"-.
#    .-----{     }--|  /,.-'-.,\  |--{     }-----.
#     )    (_)_)_)  \_/`~-===-~`\_/  (_(_(_)    (
#    (                                           )
#     )                 Oriole-DB               (
#    (                  Eric.Zhou                )
#    '-------------------------------------------'
#

import mogo
from redis import StrictRedis
from oriole.vos import get_node
from sqlalchemy import Column, Integer, String, and_, create_engine, distinct, func, or_, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

SERVICE_KEY = 'services'
ENABLE_TRX = {'twophase': True}
SERVICE_TIME = 60  # seconds
RECYCLE_TIME = 300 # seconds


def get_redis(url):
    return StrictRedis.from_url(url)


def get_mongo(db, host):
    return mogo.connect(db, host)


def get_base():
    _base = declarative_base()

    class _Base(_base):
        __abstract__ = True

        def __init__(self, **kwargs):
            for attr in self.__mapper__.column_attrs:
                key = attr.key
                if key in kwargs:
                    continue

                val = attr.columns[0].default
                if val and not callable(val.arg):
                    kwargs[key] = val.arg

            super().__init__(**kwargs)

    return _Base


def get_engine(uri):
    return create_engine(uri, pool_recycle=RECYCLE_TIME)


def get_session(bind=None, binds=None):
    _session = sessionmaker()

    if bind:
        _session.configure(bind=bind)

    if binds:
        _session.configure(binds=binds, **ENABLE_TRX)

    session = _session()
    return session


def add_service(rs, service, ver, expire=SERVICE_TIME):
    info = '%s|%s' % (get_node(), ver)
    rs.sadd(SERVICE_KEY, service)
    rs.expire(SERVICE_KEY, expire)
    rs.set(SERVICE_KEY + ':' + service, info, expire)


def get_all_services(rs):
    services = rs.smembers(SERVICE_KEY)
    ss = {}
    if services:
        services = {s.decode() for s in services}

        for s in services:
            v = rs.get(SERVICE_KEY + ':' + s)
            if v:
                ss[s] = v.decode()
    return ss
