import sqlite3
from sqlite3 import Error


class Database:
    """Database handler

    This class used to manage SQLite database.
    Table will be created while implement Table class.
    """
    DB_NAME = 'journal.db'
    succeed = False

    TYPE_Id = 'INTEGER PRIMARY KEY'
    TYPE_INTEGER = 'INTEGER'
    TYPE_REAL = 'REAL'
    TYPE_TEXT = 'TEXT'
    TYPE_BLOB = 'BLOB'
    TYPE_NULL = 'NULL'

    def __init__(self, db_name=None):
        """
        Parameters
        ----------
        db_name : str, optional
            database name (default 'journal.db')
        """
        if db_name:
            self.DB_NAME = db_name

    def exec(self, query):
        """Execute SQLite query string

        Parameters
        ----------
        query : str
            SQLite query string

        Returns
        -------
        succeed, cursor : bool,object
            Return success status and cursor value
        """
        try:
            self.succeed = True
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor = conn.cursor()
                return self.succeed, cursor.execute(query)
        except Error as e:
            self.succeed = False
            return self.succeed, e

    def drop_table(self, table_name):
        """Drop table

        Parameters
        ----------
        table_name : str
            Table name to be deleted

        Returns
        -------
        succeed : bool
            Success status
        """
        strquery = 'DROP TABLE %s' % table_name
        succeed, _ = self.exec(strquery)
        return True if succeed else False

    def rename_table(self, current_name, new_name):
        """Rename table

        Parameters
        ----------
        table_name : str
            Table name to be rename

        Returns
        -------
        succeed : bool
            Success status
        """
        strquery = 'ALTER TABLE %s RENAME TO %s' % (current_name, new_name)
        succeed, _ = self.exec(strquery)
        return True if succeed else False


class Table:
    """Table Handler

    The table created on initialize
    """
    def __init__(self, database, table_name, columns, overwrite=False):
        """
        Parameters
        ----------
        database : str
            Where this table created
        table_name : str
            Table name
        columns : dict
            Columns definition
            * {'id':'INT','name':'TEXT'}
        overwrite : bool, optional
            If exist table will be overwritten 
        """
        self.TABLE_NAME = table_name
        self.DB_NAME = database.DB_NAME

        created = self._create_table(columns, overwrite)
        if not created:
            raise Exception('Table create failed')

    def exec(self, query):
        """Execute SQLite query string

        Parameters
        ----------
        query : str
            SQLite query string

        Returns
        -------
        succeed, cursor : bool,object
            Return success status and cursor value
        """
        try:
            succeed = True
            with sqlite3.connect(self.DB_NAME) as conn:
                cursor_value = conn.execute(query)
                return succeed, cursor_value
        except Error as e:
            succeed = False
            return succeed, e

    def _create_table(self, columns, overwrite):
        created = False
        if type(columns) == type({}):
            owr = ' IF NOT EXISTS' if not overwrite else ''
            props = [' '.join([i, columns[i]]) for i in columns]
            strquery = "CREATE TABLE%s %s (%s)" % (
                owr, self.TABLE_NAME, ','.join(props))
            created, _ = self.exec(strquery)
            return created
        else:
            return created

    def add_column(self, column):
        """Add column

        Parameters
        ----------
        column : dict
            Column definition
            * {'name', 'TEXT'}

        Returns
        -------
        succeed : bool
            Return if succeed or fail
        """
        added = False
        if (type(column) == type({})) & (column.__len__() == 1):
            props = [' '.join([i, column[i]]) for i in column]
            strquery = 'ALTER TABLE %s ADD %s' % (
                self.TABLE_NAME, ','.join(props))
            added, _ = self.exec(strquery)
        else:
            return added

    def insert_row(self, **kwargs):
        """Insert data row

        Parameters
        ----------
        kwargs : column_name=data
            * id=24,name='anna'

        Returns
        -------
        succeed : bool
            Return if succeed or fail
        """
        added = False
        if kwargs.__len__() != 0:
            if 'data' in kwargs:
                data = kwargs['data']
                col_name = [name for name in data]
                col_value = ['"%s"' % data[name] for name in data]
                strquery = 'INSERT INTO %s (%s) VALUES (%s)' % (
                    self.TABLE_NAME, ','.join(col_name), ','.join(col_value))
                added, _ = self.exec(strquery)
                return added
            else:
                col_name = [name for name in kwargs]
                col_value = ['"%s"' % kwargs[name] for name in kwargs]
                strquery = 'INSERT INTO %s (%s) VALUES (%s)' % (
                    self.TABLE_NAME, ','.join(col_name), ','.join(col_value))
                added, _ = self.exec(strquery)
                return added
        else:
            return added

    def update_row(self, condition=None, **kwargs):
        """Update row
        
        Parameters
        ----------
        condition : str
            Criteria of row will be updated
            * 'id=4'
        kwargs : column_name=data
            * id=24,name='anna'
            Multiple data stored in parameter 'data'
            * data={'id':24,'name'='anna'}

        Returns
        -------
        succeed : bool
            Return if succeed or fail
        """
        updated = False
        if kwargs.__len__() != 0:
            if 'data' in kwargs:
                data = kwargs['data']
                if type(data) == type({}):
                    props = ['='.join([i, '"%s"' % data[i]]) for i in data]
                    condition = ' WHERE %s' % condition if condition else None
                    strquery = 'UPDATE %s SET %s%s' % (
                        self.TABLE_NAME, ','.join(props), condition)
                    updated, _ = self.exec(strquery)
                else:
                    raise Exception('Input invalid')
            else:
                props = ['='.join([i, '"%s"' % kwargs[i]]) for i in kwargs]
                condition = ' WHERE %s' % condition if condition else None
                strquery = 'UPDATE %s SET %s%s' % (
                    self.TABLE_NAME, ','.join(props), condition)
                updated, _ = self.exec(strquery)
            return updated
        else:
            return updated

    def delete_row(self, condition):
        """Delete row

        Parameters
        ----------
        condition: str
            Deleted row criteria
            * 'id=6'

        Returns
        -------
        succeed : bool
            Return if succeed or fail
        """
        strquery = 'DELETE from %s WHERE %s' % (self.TABLE_NAME, condition)
        deleted, _ = self.exec(strquery)
        if deleted:
            return True
        else:
            return False

    def select_row(self, columns=None, condition=None, return_kv=False):
        """Select data rows from table
        
        Parameters
        ----------
        column : list
            should be column name list
            * ['id','exc',..]
        condition : str
            Rows criteria
            * 'id=12 and name="anna"'
        return_kv : bool, optional
            Result key-value data
            * {'id':1,'name':'anna'}
        
        Returns
        -------
        data : object
            If return_kv False
        data : dict
            If return_kv True
        """
        condition = ' WHERE %s' % condition if condition else ''
        if columns:
            if type(columns) == type([]):
                columns = ','.join(columns)
            elif type(columns) == type(''):
                pass
            else:
                raise Exception('Input invalid')
        else:
            columns = '*'
        strquery = 'SELECT %s from %s%s' % (
            columns, self.TABLE_NAME, condition)
        succeed, cursor = self.exec(strquery)
        if succeed:
            if return_kv:
                if cursor:
                    h_return, h_cursor = self.exec(
                        'PRAGMA table_info(%s)' % self.TABLE_NAME)

                    header_list = [tup[1]
                                   for tup in h_cursor.fetchall()] if h_return else None

                    row_data = cursor.fetchall()
                    rows_list = []
                    for row in row_data:
                        row_kv = {}
                        for col in header_list:
                            row_kv[col] = row[header_list.index(col)]
                        rows_list.append(row_kv)
                    return rows_list
                else:
                    return None
            else:
                if cursor:
                    row_data = cursor.fetchall()

                    def col_list(row): return [col for col in row]
                    rows_list = [col_list(row) for row in row_data]
                    return rows_list
                else:
                    return None
        else:
            return None
