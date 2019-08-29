# -*- coding: utf-8 -*-

from rediscluster import StrictRedisCluster

from univider.logger import Logger
from univider.settings import redis_nodes, cache_expires

import sys
import os

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol

from univider.settings import hbase_host, hbase_port, accessid, accesskey


gen_py_path = os.path.dirname(__file__) + '/gen-py'
sys.path.append(gen_py_path)
# from hbase import THBaseService
from hbase import THBaseService4CMH
from hbase.ttypes import *

class Cacher:

    logger = Logger(__name__).getlogger()

    # redisconn = StrictRedisCluster(startup_nodes=redis_nodes)

    def set(self,key,value,expires = cache_expires):

        self.save_to_hbase(key,value)

        # try:
        #     self.redisconn.set(key,key,expires)
        #     self.save_to_hbase(key,value)
        # except Exception,e:
        #     self.logger.error("Cache set Error!")

        # finally:
        #     self.redisconn.connection_pool.disconnect()

    def get(self,key):
        # value = self.redisconn.get(key)
        value = self.read_from_hbase(key)
        # self.redisconn.connection_pool.disconnect()
        return value


    # create_namespace 'spider'
    # create 'spider:cache', {NAME => 'c', VERSIONS => 1, TTL => 86400, BLOCKCACHE => true}

    framed = False

    def save_to_hbase(self,key,value):

        socket = TSocket.TSocket(hbase_host, hbase_port)
        if self.framed:
            transport = TTransport.TFramedTransport(socket)
        else:
            transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        # client = THBaseService.Client(protocol)
        client = THBaseService4CMH.Client(protocol)

        transport.open()

        table = "spider:cache"

        if(value != None and value != ''):
            try:
                put = TPut(row=key, columnValues=[TColumnValue(family="c",qualifier="v",value=value)])
                client.put(table, put, accessid, accesskey)
            except UnicodeEncodeError,e:
                put = TPut(row=key, columnValues=[TColumnValue(family="c",qualifier="v",value=value.encode('utf8'))])
                client.put(table, put, accessid, accesskey)

        transport.close()

    def read_from_hbase(self,key):

        transport = None

        try:
            socket = TSocket.TSocket(hbase_host, hbase_port)
            if self.framed:
                transport = TTransport.TFramedTransport(socket)
            else:
                transport = TTransport.TBufferedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(transport)
            # client = THBaseService.Client(protocol)
            client = THBaseService4CMH.Client(protocol)

            transport.open()

            table = "spider:cache"

            get = TGet(row=key)
            # print "Getting:", get
            result = client.get(table, get, accessid, accesskey)

            value = result.columnValues[0].value

            transport.close()

            return value

        except Exception,e:
            try:
                transport.close()
            except Exception,e:
                pass
            return None

