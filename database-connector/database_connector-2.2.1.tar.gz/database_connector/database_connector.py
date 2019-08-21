import yaml
import cx_Oracle
import psycopg2
import pymysql
import json
from bson import json_util
import sys
if sys.version_info[0] == 3:
    import configparser
else:
    import ConfigParser as configparser


class Database_Connector(object):
    """Database Connector class"""

    def __init__(self, database, config_file):
        """
        param: database (string) Name of Database
        param: config_file (string) Path of config_file
        """
        try:
            config = self.parse_config(database=database, config_file=config_file)
            self.database = database
            self.host = config.get('host')
            self.port = config.get('port')
            self.user = config.get('user')
            self.password = config.get('password')
            self.type = config.get('type')
            self.dbname = config.get('dbname')
        except Exception as e:
            raise ValueError(f"{e}: database: {database}, config_file: {config_file}")

    def get_name(self):
        """
        returns the name of the database (str)
        """
        return str(self.database)

    def parse_config(self, database, config_file):
        """
        param database:	name of database object (str)
        param config_file:	config file (str)
        retuns dictionary with config info
        """
        stream = open(config_file, 'r')
        file_extenstion = config_file.split('.')[1]
        if file_extenstion == 'cfg':
            try:
                config = configparser.ConfigParser()
                config.read_file(stream)
                return dict(config.items(database))
            except Exception as e:
                raise configparser.NoSectionError(e)
        elif file_extenstion in ['yaml', 'yml']:
            options = yaml.safe_load(stream)
            try:
                return options[database]
            except Exception as e:
                raise KeyError(e)
        elif file_extenstion == 'json':
            options = json.load(stream)
            try:
                return options[database]
            except Exception as e:
                raise KeyError(e)
        else:
            raise ValueError('Unsupported config_file extension')

    def connect(self):
        """
        Connects to database using object properties
        """
        if self.type == "mysql":
            return pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                port=int(self.port),
                db=self.dbname
            )
        elif self.type == "postgres":
            return psycopg2.connect(
                dbname=self.dbname,
                host=self.host,
                user=self.user,
                password=self.password,
                port=int(self.port)
            )
        elif self.type == "oracle":
            return cx_Oracle.connect(f'{self.user}/{self.password}@{self.host}:{self.port}/{self.service}')

    def submit_query(self, query, connection):
        """
        param query:	SQL statement (str)
        param connection:	connection object
        """
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    def submit_variable_query(self, query, connection, var_list):
        """
        param query:	SQL statement (str)
        param connection:	connection object
        param var_list:		list of variables (list)
        """
        cursor = connection.cursor()
        cursor.execute(query, var_list)
        data = cursor.fetchall()
        cursor.close()
        return data

    def return_json_query(self, query, connection):
        """
        param query:	SQL statement (str)
        param connection:	connection object
        """
        cursor = connection.cursor()
        cursor.execute(query)
        rows = [x for x in cursor]
        cols = [x[0] for x in cursor.description]
        vals = []
        for row in rows:
            val = {}
            for k, v in zip(cols, row):
                try:
                    v = v.strip()
                except:
                    pass
                val[k] = v
            vals.append(val)
        return json.dumps(vals, default=json_util.default, sort_keys=True,
                          indent=4, separators=(',', ': '))

    def close_connection(self, connection):
        """
        param connection: connection object
        closes connection
        """
        connection.close()

    def __str__(self):
        return f"""
database: {self.database}
host: {self.host}
port: {self.port}
user: {self.user}
password: {self.password}
type: {self.type}
"""
