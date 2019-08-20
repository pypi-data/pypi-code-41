# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@version: 0.1
@author: gabriel
@file: sqlservers.py
@time: 2018/11/20 15:12
"""
from pyutils.yamls import read_from_yaml
import pymssql


class SqlserverCli:
    def __init__(self, config_file, section):
        """
        create connection to mssql
        """
        config = read_from_yaml(config_file)

        try:
            # 打开sqlserver数据库连接
            host = config[section]['Host']
            port = int(config[section]['Port'])
            user = config[section]['User']
            password = config[section]['Password']
            db_name = config[section]['Db_name']
            self.db = pymssql.connect(host=host,
                                      user=user,
                                      password=password,
                                      database=db_name,
                                      port=port,
                                      charset="utf8")
        except Exception as e:
            raise e

    def query_mssql(self, sql):
        """
        query
        """
        with self.db.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def close_mssql(self):
        """
        close connection
        """
        self.db.close()
