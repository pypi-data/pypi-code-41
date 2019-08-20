# system modules
import os
import re
import itertools
import operator
from functools import partial
import logging
import datetime
import sqlite3

# internal modules

# external modules
import attr


logger = logging.getLogger(__name__)


def sanitize(value, surround=True):
    """
    Sanitize a table or column name by replacing square and round brackets with
    curly ones and optionally surrounding the whole string in square brackets.

    Args:
        value (str): the value to sanitize
        surround (bool, optional): whether to surround the result in square
            brackets. Defaults to ``True``.
    """
    for o, n in zip("[()]", "{{}}"):
        value = value.replace(o, n)
    return "[{}]".format(value) if surround else value


@attr.s
class SQLiteDataBase:
    dbfile = attr.ib()

    datatypes = {
        None: "NULL",
        datetime.datetime: "TIMESTAMP",
        float: "REAL",
        int: "INTEGER",
        str: "TEXT",
        bytes: "BLOB",
    }
    """
    Mapping of Python :any:`type` s to SQLite types
    """

    @property
    def connection(self):
        """
        The database connection. Is created automatically if used.
        """
        try:
            return self._connection
        except AttributeError:
            logger.debug("opening database {}...".format(repr(self.dbfile)))
            conn = sqlite3.connect(
                self.dbfile,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
            conn.row_factory = sqlite3.Row
            logger.debug("database {} opened".format(repr(self.dbfile)))
            self._connection = conn
        return self._connection

    @property
    def tables(self):
        """
        Get all tables
        """
        return {
            name: self.get_table(name)
            for name in map(
                operator.itemgetter(0),
                self.table_select(
                    table="sqlite_master",
                    what=("name",),
                    condition="type='table'",
                ),
            )
        }

    def create_table(self, name, fields):
        """
        Create a new table

        Args:
            name (str): the new table name. Will be :any:`sanitize` d.
            fields (dict): mapping of column names to datatypes as in
                :any:`SQLiteDataBase.datatypes`.
        """
        f = ",".join(
            (
                " ".join(
                    (sanitize(c), self.datatypes.get(t, self.datatypes[bytes]))
                )
                for c, t in fields.items()
            )
        )
        sql = "CREATE TABLE {name} ({fields})".format(
            name=sanitize(name), fields=f
        )
        self(sql)
        return self[name]

    def table_select(self, table, what="*", condition=None, parameters=None):
        """
        Execute a ``SELECT`` query

        Args:
            what (str or tuple of str, optional): what to select. Either an SQL
                expression string or a tuple of column name strings which will
                be :any:`sanitize` d.
            condition (str, optional): condition to apply. Is appended with
                ``WHERE``.
            parameters (tuple or dict, optional): If the ``condition`` contains
                substitutable parameters (like ``?`` or ``:param``), they can
                be specified here.
        """
        sql = "SELECT {what} FROM {table}{condition}".format(
            what=what
            if isinstance(what, str)
            else ",".join(map(sanitize, what)),
            table=sanitize(table),
            condition=" WHERE {}".format(condition) if condition else "",
        )
        return self(sql, parameters) if parameters else self(sql)

    def table_get_columns(self, table):
        """
        Determine the available columns in a table

        .. warning::

            This implementation is based on very simlple regular expressions
            and might not work except for tables created with the
            :any:`SQLiteDataBase` class itself.

        Args:
            table (str): the table

        Returns:
            tuple of str: the columns
        """
        result = self.table_select(
            table="sqlite_master",
            what=("sql",),
            condition="type = 'table' AND name = :name",
            parameters={"name": sanitize(table, surround=False)},
        )
        sql = next(iter(next(result, tuple())), "")
        column_definitions = re.search(r"\(([^)]+)\)", sql).groups()[0]
        columns = re.findall(r"\[([^\]]+)\]", column_definitions)
        return tuple(columns)

    def table_add_column(self, table, column, datatype):
        """
        Add a column to a table

        Args:
            table (str): the table name. Will be :any:`sanitize` d.
            column (str): the column name. Will be :any:`sanitize` d.
            datatype (type): the data type. Should be contained in
                :any:`SQLiteDataBase.datatypes`
        """
        sql = "ALTER TABLE {table} ADD {column} {datatype}".format(
            table=sanitize(table),
            column=sanitize(column),
            datatype=self.datatypes.get(datatype, self.datatypes[bytes]),
        )
        return self(sql)

    def table_insert(self, table, data):
        """
        Insert data into a table

        Args:
            table (str): the table name. Will be :any:`sanitize` d.
            data (dict): mapping of column names (which will be
                :any:`sanitize` d) to values to store. If a column does not yet
                exist in the given table, it will be created with
                :any:`table_add_column` with the type of the value as datatype.
        """
        data = {sanitize(k, surround=False): v for k, v in data.items()}
        existing_columns = self.table_get_columns(table)
        unexisting_columns = set(data.keys()) - set(existing_columns)
        for column in unexisting_columns:
            logger.info(
                "Database {dbfile}: "
                "Adding column {column} to table {table}".format(
                    dbfile=repr(self.dbfile),
                    table=repr(table),
                    column=repr(column),
                )
            )
            self.table_add_column(
                table=table, column=column, datatype=type(data[column])
            )
        sql = "INSERT INTO {table} ({columns}) VALUES ({values})".format(
            table=sanitize(table),
            columns=",".join(map(sanitize, data.keys())),
            values=",".join(itertools.repeat("?", len(data))),
        )
        return self(sql, tuple(data.values()))

    def table_exists(self, name):
        """
        Determine whether a table exists

        Args:
            name (str): the name of the table

        Returns:
            bool : whether a table with the given name exists
        """
        if name == "sqlite_master":
            return True
        result = self.table_select(
            table="sqlite_master",
            what="count(*)",
            condition="type = 'table' AND name = :name",
            parameters={"name": sanitize(name, surround=False)},
        )
        return next(iter(next(result, tuple())), None) == 1

    def get_table(self, name):
        return Table(name=name, database=self)

    def __getitem__(self, name):
        """
        When indexed, return the corresponding :any:`Table`

        Raises:
            KeyError: If no such table exists
        """
        if name not in self:
            raise KeyError(
                "No such table {name} in database {dbfile}".format(
                    name=repr(name), dbfile=repr(self.dbfile)
                )
            )
        return self.get_table(name)

    def __contains__(self, name):
        """
        Checks whether a table exists in the database
        """
        return self.table_exists(name)

    def __call__(self, cmd, parameters=None):
        """
        When called, execute a given SQL command and optionally hand in
        parameters.

        Args:
            cmd (str): the SQL command to execute
            parameters (tuple or dict, optional): the parameters to substitute
        """
        with self.connection as conn:
            if parameters is None:
                logger.debug(
                    "Database {dbfile}: executing: {cmd}".format(
                        dbfile=repr(self.dbfile), cmd=cmd
                    )
                )
                return conn.execute(cmd)
            else:
                logger.debug(
                    "Database {dbfile}: executing "
                    "with parameters {params}: {cmd} ".format(
                        dbfile=repr(self.dbfile), cmd=cmd, params=parameters
                    )
                )
                return conn.execute(cmd, parameters)

    def close(self):
        """
        Close the database connection
        """
        if hasattr(self, "_connection"):
            logger.debug(
                "closing database {dbfile}...".format(dbfile=repr(self.dbfile))
            )
            try:
                self.connection.close()
            except sqlite3.ProgrammingError as e:
                pass
            logger.debug(
                "database {dbfile} closed.".format(dbfile=repr(self.dbfile))
            )
            del self._connection

    def __del__(self):
        """
        When the object goes out of scope, :any:`close` the database
        """
        self.close()


@attr.s(frozen=True)
class Table:
    """
    Convenience class representing a table in a :any:`SQLiteDataBase`.

    Args:
        name (str): the name of the table
        database (SQLiteDataBase): the database this table lives in
    """

    name = attr.ib(validator=attr.validators.instance_of(str))
    database = attr.ib(validator=attr.validators.instance_of(SQLiteDataBase))

    @property
    def exists(self):
        """
        Wrapper for :any:`table_exists` with this :attr:`Table.name` set as
        default table name.
        """
        return self.database.table_exists(self.name)

    @property
    def columns(self):
        """
        Wrapper for :any:`table_get_columns` with this :attr:`Table.name` set
        as default table name.
        """
        return self.database.table_get_columns(self.name)

    def create(self, *args, **kwargs):
        """
        Wrapper for :any:`create_table` with this :attr:`Table.name` set as
        default table name.
        """
        return partial(self.database.create_table, name=self.name)(
            *args, **kwargs
        )

    def add_column(self, *args, **kwargs):
        """
        Wrapper for :any:`table_add_column` with this :attr:`Table.name` set as
        default table name.
        """
        return partial(self.database.table_add_column, table=self.name)(
            *args, **kwargs
        )

    def select(self, *args, **kwargs):
        """
        Wrapper for :any:`table_select` with this :attr:`Table.name` set as
        default table name.
        """
        return partial(self.database.table_select, table=self.name)(
            *args, **kwargs
        )

    def insert(self, *args, **kwargs):
        """
        Wrapper for :any:`table_insert` with this :attr:`Table.name` set as
        default table name.
        """
        return partial(self.database.table_insert, table=self.name)(
            *args, **kwargs
        )
