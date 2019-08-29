# -*- coding: utf-8 -*-

import sys
import os

import datetime

from hdfs import HdfsError
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol

from univider.settings import hbase_host, hbase_port, accessid, accesskey, hdfs_dir, hdfs_user, hdfs_web

from hdfs.client import InsecureClient

gen_py_path = os.path.dirname(__file__) + '/gen-py'
sys.path.append(gen_py_path)
# from hbase import THBaseService
from hbase import THBaseService4CMH
from hbase.ttypes import *

class Storager:

    # create_namespace 'spider'
    # create 'spider:cplatform', {NAME => 'w', VERSIONS => 1, TTL => 2592000, BLOCKCACHE => true}

    framed = False

    def save_to_hbase(self,key,url,title,content):

        socket = TSocket.TSocket(hbase_host, hbase_port)
        if self.framed:
            transport = TTransport.TFramedTransport(socket)
        else:
            transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        # client = THBaseService.Client(protocol)
        client = THBaseService4CMH.Client(protocol)

        transport.open()

        table = "spider:cplatform"
        if(url != None and url != ''  ):
            put = TPut(row=key, columnValues=[TColumnValue(family="w",qualifier="u",value=url)])
            client.put(table, put, accessid, accesskey)
        if(title != None and title != ''  ):
            try:
                put = TPut(row=key, columnValues=[TColumnValue(family="w",qualifier="t",value=title)])
                client.put(table, put, accessid, accesskey)
            except UnicodeEncodeError,e:
                put = TPut(row=key, columnValues=[TColumnValue(family="w",qualifier="t",value=title.encode('utf8'))])
                client.put(table, put, accessid, accesskey)

        if(content != None and content != ''  ):
            try:
                put = TPut(row=key, columnValues=[TColumnValue(family="w",qualifier="c",value=content)])
                client.put(table, put, accessid, accesskey)
            except UnicodeEncodeError,e:
                put = TPut(row=key, columnValues=[TColumnValue(family="w",qualifier="c",value=content.encode('utf8'))])
                client.put(table, put, accessid, accesskey)

        # print "Putting:", put

        transport.close()

    def read_from_hbase(self,key):

        socket = TSocket.TSocket(hbase_host, hbase_port)
        if self.framed:
            transport = TTransport.TFramedTransport(socket)
        else:
            transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        # client = THBaseService.Client(protocol)
        client = THBaseService4CMH.Client(protocol)

        transport.open()

        table = "spider:cplatform"

        get = TGet(row=key)
        print "Getting:", get
        result = client.get(table, get, accessid, accesskey)

        print "Result:", result

        transport.close()

    def save_to_hdfs(self,key,url,title,content):
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        hdfs_path = hdfs_dir + current_date
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
        data = "\n"+key+"\n"+url+"\n"
        if(title != None and title != ''  ):
            data = data + title+"\n"
        if(content != None and content != ''  ):
            data = data + content+"\n"
        try:
            client = InsecureClient(hdfs_web, user=hdfs_user)
            client.write(hdfs_path=hdfs_path, data=data, append=True)
        except HdfsError,e:
            client.write(hdfs_path=hdfs_path, data=data)
