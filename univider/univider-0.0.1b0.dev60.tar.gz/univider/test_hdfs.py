# -*- coding: utf-8 -*-
import datetime

from hdfs import HdfsError
from hdfs.client import Client, InsecureClient

# client = Client("http://master.hadoop:50070")

client = InsecureClient('http://master.hadoop:50070', user='hadoop')

# print dir(client)

# print client.list("/user")

# print client.makedirs("/tmp/test")

client.delete('/user/spider', recursive=True)

# current_date = datetime.datetime.now().strftime("%Y%m%d")
#
# hdfs_dir = "/user/a/b/c/"
#
# hdfs_path = hdfs_dir + current_date
#
# data = "\n测试"
#
# try:
#     client.write(hdfs_path=hdfs_path, data=data, append=True)
# except HdfsError,e:
#     client.write(hdfs_path=hdfs_path, data=data)



