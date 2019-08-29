# -*- coding: utf-8 -*-

import redis_extensions as redis


def redis_conf(conf):
    return {
        'host': conf.get('HOST', 'localhost'),
        'port': conf.get('PORT', 6379),
        'password': '{}:{}'.format(conf.get('USER', ''), conf.get('PASSWORD', '')) if conf.get('USER') else '',
        'db': conf.get('db', 0),
        'decode_responses': conf.get('decode_responses', False),
    }


def connector(conf):
    return redis.StrictRedisExtensions(connection_pool=redis.ConnectionPool(**redis_conf(conf)))


redis_connect = connector
