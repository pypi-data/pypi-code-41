# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zhanglanhui
hive
"""
from pyhive import hive
from pyutils.yamls import read_from_yaml


class HiveCli:
    def __init__(self, config_file, section, authMechanism="KERBEROS"):
        """
        create connection to hive server2
        """
        config = read_from_yaml(config_file)

        try:
            host = config[section]['Host']
            port = int(config[section]['Port'])
            db_name = config[section]['Db_name']
            self.conn = hive.connect(host=host,
                                     port=port,
                                     auth=authMechanism,
                                     kerberos_service_name="hive",
                                     database=db_name)
        except Exception as e:
            raise e

    def query_hive(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def close_hive(self):
        """
        close connection
        """
        self.conn.close()
