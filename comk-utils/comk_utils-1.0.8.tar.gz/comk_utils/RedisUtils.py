import json

import redis


class RedisUtils():

    def __init__(self, host='localhost', port=6379, db=1, decode_responses=True):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = decode_responses
        self.r = None
        self.pool = None

    def get_redis_link(self):
        '''
        直接获取 redis 连接

        :return:
        '''
        if self.r:
            return self.r
        else:
            # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379，这里用docker启动，端口为6378
            # 加上decode_responses=True，写入的键值对中的value为str类型，不加这个参数写入的则为字节类型。
            self.r = redis.Redis(host=self.host, port=self.port, db=self.db, decode_responses=self.decode_responses)
            return self.r

    def get_redis_connection_pool_link(self):
        '''
        获取连接池中的连接

        :return:
        '''
        if not self.pool:
            self.pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, decode_responses=True)
        if not self.r:
            self.r = redis.Redis(connection_pool=self.pool)
        return self.r

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        '''
        对 redis 的 set 的重写，使其能保存dict和list。

        :return:
        '''
        r = self.get_redis_connection_pool_link()
        if value != None:
            value = json.dumps(value)
            return r.set(name, value, ex, px, nx, xx)
        else:
            return self.delete(name)

    def get(self, name):
        '''
        对 redis 的 get 的重写，使其返回正常的dict和list。

        :param name:
        :return:
        '''
        r = self.get_redis_connection_pool_link()
        value = r.get(name)
        if value:
            return json.loads(value)
        else:
            return value

    def delete(self, names):
        '''
        删除

        :param names:
        :return:
        '''
        r = self.get_redis_connection_pool_link()
        return r.delete(names)

    def ttl(self, name):
        '''
        显示过期时间

        :param name:
        :return:
        '''
        r = self.get_redis_connection_pool_link()
        return r.ttl(name)
