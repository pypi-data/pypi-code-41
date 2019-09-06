"""
MS SQL Database Backend for Django 2.x
"""
from django.db.backends.base.base import BaseDatabaseWrapper
import pymssql

from .pyodbc import base as odbc


class DatabaseOperations(odbc.DatabaseOperations):
    compiler_module = 'django_mssql2.pyodbc.compiler'

    def regex_lookup(self, lookup_type):
        pass


class DatabaseWrapper(odbc.DatabaseWrapper):
    Database = pymssql

    driver_charset = 'utf-8'
    supports_mars = False

    ops_class = DatabaseOperations

    def __init__(self, *args, **kwargs):
        BaseDatabaseWrapper.__init__(self, *args, **kwargs)

    def get_connection_params(self):
        params = {
            'host': self.settings_dict['HOST'],
            'database': self.settings_dict['NAME'],
            'user': self.settings_dict['USER'],
            'password': self.settings_dict['PASSWORD'],
            'port': self.settings_dict['PORT'],
        }
        options = self.settings_dict.get('OPTIONS', {})
        params.update(options)
        return params

    def get_new_connection(self, conn_params):
        return self.Database.connect(**conn_params)

    def create_cursor(self, name=None):
        return CursorWrapper(self.connection.cursor(), self)

    def init_connection_state(self):
        # Not calling super() because we don't care much about version checks.
        pass

    def _get_trancount(self):
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT @@TRANCOUNT')
            return cursor.fetchone()[0]

    def _set_autocommit(self, autocommit):
        self.connection.autocommit(autocommit)


class CursorWrapper(odbc.CursorWrapper):

    def format_sql(self, sql, params):
        return sql
