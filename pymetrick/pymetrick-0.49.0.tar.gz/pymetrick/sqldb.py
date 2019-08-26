#!/usr/bin/python
# -*- coding: utf-8 *-*

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

'''Modulo para gestionar datos en MySQL'''

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2015-06-26'
__credits__ = ''
__text__ = 'Gestion de datos en BBDD'
__file__ = 'sqldb.py'

#--- CHANGES ------------------------------------------------------------------
# 2015-06-26 v0.01 PL: - First version
# 2015-09-10 v0.03 PL: - Adaptado a python 3.x
# 2017-10-02 v0.43 PL: - Migrar a PYTHON 3.6


import sys
import os
import re
import time
import logging
import logging.handlers

try:
    from importlib import import_module  # Python 3.4+ 
except ImportError:
    print('''IMPORTLIB not installed''')
"""    
# MySQL
try:
    import mysql.connector
    from mysql.connector import Error
    from mysql.connector import errorcode
except:
    print('''MYSQL.CONNECTOR not installed!''')
    
# postgreSQL
try:
    import psycopg2
except:
    print('''PSYCOPG2 not installed!''')
"""

RETRY_NUMBER = 50   # Cuantas veces intenta reconectar
RETRY_SLEEP  = 60   # Tiempo de espera

BLACKLIST = ["--",";--",";","/*","*/","@@"," @","1=1",
             "char","nchar","varchar","nvarchar",
             "alter","begin","cast","create","cursor","declare","delete","drop","end","exec","execute",
             "fetch","insert","kill","open",
             "select", "sys","sysobjects","syscolumns",
             "table","update","<script","</script"]

SQL_OPERATORS = [
    '=',
    '!=',
    'like',
    'not like',
    'ilike',
    'not ilike',
    'in',
    'not in',
    '<=',
    '>=',
    '<',
    '>',
    ]

# PY3
long = int

# Check development code
DEBUG = True


'''
DEBUG - debug message
INFO - info message
WARNING - warn message
ERROR - error message
CRITICAL - critical message
'''
LOG_FILENAME = '-'.join([os.path.abspath(__file__).split(os.sep)[len(os.path.abspath(__file__).split(os.sep))-1],])[:-3]
LOG = logging.getLogger(LOG_FILENAME)

if 'LD_LIBRARY_PATH' in list(os.environ.keys()):
    # CGI environment
    sys.stdout = sys.stderr
    if DEBUG:
        logging.basicConfig(stream = sys.stderr, level=logging.DEBUG, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(stream = sys.stderr, level=logging.WARNING, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
else:
    # not CGI environment
    logging.basicConfig(stream=sys.stderr)
    hdlr = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME+'.log',mode='a', encoding='utf-8', maxBytes=1048576, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    LOG.addHandler(hdlr)
    if DEBUG:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARNING)
        
def sanitizeSQL(_string_):
    '''Limpiar datos con los que se realiza algun tipo de acceso a la base de datos'''
    '''_obj_ = re.compile('|'.join([re.escape(n) for n in BLACKLIST]), flags=re.IGNORECASE)
    return _obj_.sub("", _string_) '''
    return _string_

class SQLdb(object):
    __instance__ = None

    start_time = time.time()
    query_time = 0

    _sql_driver = None
    _sql_driver_extras = None
    _sql_driver_errorcode = None
    connect = None       # connector
    cursor = None        # cursor


    value_type = {'CHAR':'text',
                 'VARCHAR':'text',
                 'TINYBLOB':'text',
                 'TINYTEXT':'text',
                 'BLOB':'text',
                 'TEXT':'text',
                 'MEDIUMBLOB':'text',
                 'MEDIUMTEXT':'text',
                 'LONGBLOB':'text',
                 'LONGTEXT':'text',
                 'TINYINT':'int',
                 'SMALLINT':'int',
                 'MEDIUMINT':'int',
                 'INT':'int',
                 'INTEGER':'int',
                 'BIGINT':'long',
                 'FLOAT':'float',
                 'DOUBLE':'float',
                 'REAL':'float',
                 'DECIMAL':'decimal',
                 'NUMERIC':'decimal',
                 'DATE':'date',
                 'DATETIME':'datetime',
                 'TIMESTAMP':'datetime',
                 'TIME':'float',
                 'YEAR':'int'}

    field_type = {0: 'DECIMAL',
                  1: 'TINY',
                  2: 'SHORT',
                  3: 'LONG',
                  4: 'FLOAT',
                  5: 'DOUBLE',
                  6: 'NULL',
                  7: 'TIMESTAMP',
                  8: 'LONGLONG',
                  9: 'INT24',
                 10: 'DATE',
                 11: 'TIME',
                 12: 'DATETIME',
                 13: 'YEAR',
                 14: 'NEWDATE',
                 15: 'VARCHAR',
                 16: 'BIT',
                246: 'NEWDECIMAL',
                247: 'INTERVAL',
                248: 'SET',
                249: 'TINY_BLOB',
                250: 'MEDIUM_BLOB',
                251: 'LONG_BLOB',
                252: 'BLOB',
                253: 'VAR_STRING',
                254: 'STRING',
                255: 'GEOMETRY' }


    def __new__(cls, *args, **kwargs):
        if SQLdb.__instance__ is None:
            SQLdb.__instance__ = object.__new__(cls)
        SQLdb.__instance__.args = args
        SQLdb.__instance__.kwargs = kwargs
        return SQLdb.__instance__


    def __init__(self,*args, **kwargs):
        '''Abrir acceso a bbdd'''
        self.connect = None;
        self.cursor = None;
        self.config = dict()
        
        self.driver = kwargs['driver'] if kwargs.get('driver',None) else 'mysql';
        self.config['database'] = kwargs['database']
        self._key_delim = '"';
        self._str_delim = "'";

        if self.driver == 'mysql':
            self.config['host'] = kwargs['host'] if kwargs.get('host',None) else '127.0.0.1';
            self.config['port'] = kwargs['port'] if kwargs.get('port',None) else '3306';
            self.config['user'] = kwargs['username']
            self.config['password'] = kwargs['password']
            self._key_delim = '`';
            self.config['time_zone'] = kwargs['time_zone'] if kwargs.get('time_zone',None) else "+0:00";
            self.config['sql_mode'] = kwargs['sql_mode'] if kwargs.get('sql_mode',None) else "TRADITIONAL";
            self.config['charset'] = kwargs['charset'] if kwargs.get('charset',None) else "utf8";
            self.config['collation'] = kwargs['collation'] if kwargs.get('collation',None) else "utf8_spanish_ci";
            self.config['compress'] = kwargs['compress'] if kwargs.get('compress',None) else False;
            self.config['autocommit'] = kwargs['autocommit'] if kwargs.get('autocommit',None) else True;
            self.config['raise_on_warnings']= kwargs['raise_on_warnings'] if kwargs.get('raise_on_warnings',None) else True;
            self.config['use_unicode'] = kwargs['use_unicode'] if kwargs.get('use_unicode',None) else True;
            self.config['get_warnings'] = kwargs['get_warnings'] if kwargs.get('get_warnings',None) else True;
            self.config['buffered'] = kwargs['buffered'] if kwargs.get('buffered',None) else True;
        elif self.driver == 'postgresql':
            self.config['host'] = kwargs['host'] if kwargs.get('host',None) else '127.0.0.1';
            self.config['port'] = kwargs['port'] if kwargs.get('port',None) else '5432';
            self.config['user'] = kwargs['username']
            self.config['password'] = kwargs['password']
        elif self.driver == 'sqlite3':
            '''sqlite3.connect(database[, timeout, detect_types, isolation_level, check_same_thread, factory, cached_statements, uri])'''
            pass
        else:
            LOG.error('Driver Error Unknown database driver !!!')
            raise Exception("Unknown database driver")

        if self.driver == 'mysql':
            try:
                self._sql_driver = import_module('mysql.connector')
                self._sql_driver_errorcode = import_module('.errorcode', package='mysql.connector')
            except:
                LOG.error('MYSQL.CONNECTOR not installed !!!')
                print('''MYSQL.CONNECTOR not installed!''')
        elif self.driver == 'postgresql':
            try:
                self._sql_driver = import_module('psycopg2')
                self._sql_driver_extras = import_module('psycopg2.extras')
            except:
                LOG.error('PSYCOPG2 not installed !!!')
                print('''PSYCOPG2 not installed!''')
        elif self.driver == 'sqlite3':
            try:
                self._sql_driver = import_module('sqlite3')
            except:
                LOG.error('SQLITE3 not installed !!!')
                print('''SQLITE3 not installed!''')

        # self.rows permite obtener las filas afectadas
        self.rows = 0
        self.lastId = 0

        try:
            self.reconnect()
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))

    def __del__(self):
        self.close()

    def close(self):
        '''Cierra la conexion a la base de datos'''
        try:
            if getattr(self,"connect",None):
                if getattr(self,"cursor",None):
                    self.cursor.close()
                    self.cursor = None
                #closing database connection.
                if(self.connect.is_connected()):
                    self.connect.close()
                    self.connect = None
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))

    def reconnect(self):
        '''Cierra la conexion con la base de datos y vuelve a abrirla'''
        try:
            self.close()
            if self.driver == 'mysql':
                self.connect = self._sql_driver.connect(**self.config)
                self.cursor = self.connect.cursor()
                #self.set_wait_timeout
                return True
            elif self.driver == 'postgresql':
                self.connect = self._sql_driver.connect(**self.config)
                #conn = psycopg2.connect(database='test',user='postgres',password='pass', host='localhost')
                self.cursor = self.connect.cursor()
                return True
            elif self.driver == 'sqlite3':
                '''sqlite3.connect(database[, timeout, detect_types, isolation_level, check_same_thread, factory, cached_statements, uri])'''
                self.connect = self._sql_driver.connect(**self.config)
                #con = sqlite3.connect(":memory:")
        except self._sql_driver.Error as e:
            if e.errno == self._sql_driver_errorcode.ER_ACCESS_DENIED_ERROR:
                tb = sys.exc_info()[2]
                LOG.error("{0} Something is wrong with your user name or password, in line {1} !!!".format(repr(e),tb.tb_lineno))
            elif e.errno == self._sql_driver_errorcode.ER_BAD_DB_ERROR:
                tb = sys.exc_info()[2]
                LOG.error("{0} Database does not exist, in line {1} !!!".format(repr(e),tb.tb_lineno))
            elif e.errno == self._sql_driver_errorcode.CR_CONNECTION_ERROR:
                tb = sys.exc_info()[2]
                LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            elif e.errno == self._sql_driver_errorcode.CR_LOCALHOST_CONNECTION:
                tb = sys.exc_info()[2]
                LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            else:
                tb = sys.exc_info()[2]
                LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False
        except self._sql_driver.OperationalError as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False

    def execute(self, sql=None , parameters=None):
        '''Ejecuta consultas teniendo en cuenta transacciones
           sql parametro con el codigo
           parameters son las variables que se pueden incorporar al codigo sql
        '''
        try:
            self.is_connect()
            if sql:
                if self.config['autocommit']:
                    self.connect.start_transaction()
                """    
                # identificar warnings
                warnings = self.cursor.fetchwarnings()
                if warnings:
                    ids = [ i for l,i,m in warnings]
                    del warnings
                    if 1266 in ids:
                        LOG.debug('''Table was created as MYISAM, no transaction support. Bailing out, no use to continue. Make sure InnoDB is available!''')
                        self.connect.close()
                        return None
                """  
                if parameters is not None:
                    if DEBUG:
                        LOG.debug('query {0}'.format(sql % parameters,))
                    if isinstance(parameters[0],(list,tuple)):
                        self.cursor.executemany(sql, parameters)
                    else:
                        self.cursor.execute(sql, parameters)
                else:
                    if DEBUG:
                        LOG.debug('query {0}'.format(sql,))
                    self.cursor.execute(sql)

                if sql[0:6].upper()=='''INSERT''':
                    # Informa de num. de ultima fila autoincremental
                    if hasattr(self.connect,"commit"):
                        self.connect.commit()
                    self.lastId = self.cursor.lastrowid
                    return self.lastId

                elif sql[0:6].upper()=='''UPDATE''' or sql[0:6].upper()=='''DELETE''':
                    # Informa de num. filas afectadas
                    if hasattr(self.connect,"commit"):
                        self.connect.commit()
                    self.rows = self.cursor.rowcount
                    # is rows = -1 not cursor.execute
                    return self.rows

                elif sql[0:6].upper()=='''SELECT''':
                    # Devuelve informacion de todas las filas seleccionadas
                    return self.cursor.fetchall()

        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            if not self.config['autocommit']:
                self.connect.rollback()
        finally:
            self.close()

    def set_auto_increment(self,table=None,id=1):
        '''Fija el autoincremento en la tabla correspondiente al parametro'''
        self.is_connect()
        try:
            if table is not None:
                table_list = self.show_tables()
                if isinstance(table_list,(list,tuple)):
                    if (table,) in table_list:
                        self.cursor.execute('''ALTER TABLE {0} AUTO_INCREMENT = {1}'''.format(table,id))
                        # identificar warnings
                        warnings = self.cursor.fetchwarnings()
                        if warnings:
                            del warnings
                            ids = [ i for l,i,m in warnings]
                            LOG.debug('''{0}'''.format(ids))
                        return True
            return False
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False
        finally:
            self.close()

    def set_wait_timeout(self,seconds=29000):
        '''Fija wait_timeout y interactive_timeout a 60 por defecto'''
        ''' IMPORTANTE no funciona correctamente '''
        self.is_connect()
        try:
            if seconds is not None:
                print(self.cursor.execute("SET wait_timeout=={}".format(seconds)))
                print(self.cursor.execute("SET GLOBAL wait_timeout=={}".format(seconds)))
                print(self.cursor.execute("SET SESSION wait_timeout=={}".format(seconds)))
                print(self.cursor.execute("set interactive_timeout={}".format(seconds)))
            return
        except Exception as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False


    def set_optimize(self,table=None):
        '''Optimizacion de tablas INNODB'''
        try:
            if table is not None:
                table_list = self.show_tables()
                if isinstance(table_list,(list,tuple)):
                    if (table,) in table_list:
                        self.is_connect()
                        self.cursor.execute('''OPTIMIZE TABLE {};'''.format(table))
                        # identificar warnings
                        warnings = self.cursor.fetchwarnings()
                        if warnings:
                            print((wargings,))
                            ids = [ i for l,i,m in warnings]
                            LOG.debug('''{0}'''.format(ids))
                        return True
            return False
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False
        finally:
            self.close()

    def show_version(self):
        '''Version de MySQL'''
        self.is_connect()
        try:
            self.cursor.execute('''SELECT VERSION();''')
            return self.cursor.fetchone()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return list()
        finally:
            self.close()

    def create_database(self,database=None):
        '''create database'''
        self.is_connect()
        try:
            if database is not None:
                self.cursor.execute('''CREATE DATABASE IF NOT EXISTS {};'''.format(database))
                return True
            return False
        except self._sql_driver.Error as e:
            if e.errno == errorcode.ER_CANT_CREATE_DB:
                tb = sys.exc_info()[2]
                LOG.error("not create db {0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            else:
                tb = sys.exc_info()[2]
                LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            return False
        finally:
            self.close()

    def create_table(self,table):
        '''Crear una tabla'''
        self.is_connect()
        try:
            pass
        except self._sql_driver.Error as e:
            if e.errno == errorcode.ER_CANT_CREATE_TABLE:
                tb = sys.exc_info()[2]
                LOG.error("not create table {0} in line {1} !!!".format(repr(e),tb.tb_lineno))
            else:
                tb = sys.exc_info()[2]
                LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))

    def show_database(self):
        '''Obtener database name'''
        self.is_connect()
        try:
            self.cursor.execute('''SELECT DATABASE();''')
            return self.cursor.fetchall()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()
           

    def show_tables(self):
        '''Ver lista de tablas'''
        self.is_connect()
        try:
            self.cursor.execute('''SHOW TABLES;''')
            return self.cursor.fetchall()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()

    def show_columns(self, table=None):
        '''Ver lista de columnas'''
        try:
            if table is not None:
                table_list = self.show_tables()
                if isinstance(table_list,(list,tuple)):
                    if (table,) in table_list:
                        self.is_connect()
                        self.cursor.execute('''SHOW COLUMNS FROM {};'''.format(table))
                        return self.cursor.fetchall()
            return list()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()

    def show_index(self, table=None):
        '''Ver lista de indices'''
        try:
            if table is not None:
                table_list = self.show_tables()
                if isinstance(table_list,(list,tuple)):
                    if (table,) in table_list:
                        self.is_connect()
                        self.cursor.execute('''SHOW INDEX FROM {};'''.format(table))
                        return self.cursor.fetchall()
            return list()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()


    def show_vars(self):
        '''Ver lista de variables'''
        try:
            self.is_connect()
            self.cursor.execute('''SHOW VARIABLES;''')
            return self.cursor.fetchall()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()

    def show_process(self):
        '''Ver lista de procesos del usuario'''
        try:
            self.is_connect()
            self.cursor.execute('''SHOW PROCESSLIST WHERE USER LIKE {};'''.format(self._db_args['user']))
            return self.cursor.fetchall()
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        finally:
            self.close()

    def is_connect(self):
        ''' Comprueba conexion a bb.dd. '''
        try:
            retry = 0
            while retry < RETRY_NUMBER:
                try:
                    if self.reconnect():
                       # si la reconexion es correcta
                       retry = RETRY_NUMBER
                except self._sql_driver.Error as e:
                    if e.errno == self._sql_driver_errorcode.CR_CONNECTION_ERROR:
                        tb = sys.exc_info()[2]
                        LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
                    elif e.errno == self._sql_driver_errorcode.CR_LOCALHOST_CONNECTION:
                        tb = sys.exc_info()[2]
                        LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
                    else:
                        tb = sys.exc_info()[2]
                        LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
                    time.sleep(RETRY_SLEEP)
                except self._sql_driver.OperationalError as e:
                    tb = sys.exc_info()[2]
                    LOG.error("{0} in line {1} !!!".format(repr(e.diag.message_detail),tb.tb_lineno))
                    time.sleep(RETRY_SLEEP)
                retry += 1
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e),tb.tb_lineno))
        except self._sql_driver.OperationalError as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e.diag.message_detail),tb.tb_lineno))
        except self._sql_driver.Error as e:
            tb = sys.exc_info()[2]
            LOG.error("{0} in line {1} !!!".format(repr(e.diag.message_detail),tb.tb_lineno))
            #print e.pgerror
            #print e.diag.message_detail

if __name__ == "__main__":
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
        Gestion de BB.DD. en MySQL o MariaDB o POSTGRESQL :\n\n''')

