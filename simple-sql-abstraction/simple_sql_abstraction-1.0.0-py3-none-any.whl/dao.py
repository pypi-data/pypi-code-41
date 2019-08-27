from simple_sql_abs.singleton import Singleton
from contextlib import closing
import sqlite3
import pyclbr


class BaseDao(Singleton):
    """
    A class that defines methods that facilitate
    insert, update, delete and selet commands in sqlite3 databases.

    Methods
    -------
    delete(DumbTable, id=1)
        execute an delete command on the database

    update(dumb_record, dumb_value=5)
        execute an update command on the database

    update(new_dumb_record)
        execute an insert command on the database

    select(DumbTable, id=1, dumb_value=5)
        execute an insert command on the database
    """

    def __init__(self):
        self._connection_manager = ConnectionManager.instance

    def __create_where_clause(self, **where_dict):
        if len(where_dict) > 0:
            where_parameters = [k + " in ?" if isinstance(where_dict[k], tuple)
                                or isinstance(where_dict[k], list)
                                else k + "=" + "?" for k in where_dict.keys()]
            where_parameters_values = [tuple(v) if isinstance(v, list) else v
                                       for v in where_dict.values()]
            return [" where " + " and ".join(where_parameters),
                    where_parameters_values]
        else:
            return ["", []]

    def delete(self, delete_type, **where_dict):
        """
        Parameters
        ----------
        delete_type : type
           Type that represents the databse table

        **where_dict :
           **kwargs parameter with the values to the where clause
        """

        if ConnectionManager.instance.in_memory:
            self.__delete_not_closing(ConnectionManager.instance.conn,
                                      delete_type, **where_dict)
        else:
            with closing(self._connection_manager.get_connection()) as conn:
                with conn as cursor:
                    self.__delete_not_closing(cursor, delete_type,
                                              **where_dict)

    def __delete_not_closing(self, cursor, delete_type, **where_dict):
        delete_sql = "delete from " + delete_type.__name__
        result_where = self.__create_where_clause(**where_dict)
        cursor.execute(delete_sql + result_where[0], tuple(result_where[1]))

    def update(self, obj, **where_dict):
        """
        Parameters
        ----------
        obj : ?
           instance of the Type that represents the databse table
           that will be updated

        **where_dict :
           **kwargs parameter with the values to the where clause
        """

        if ConnectionManager.instance.in_memory:
            ret = self.__update_not_closing(ConnectionManager.instance.conn,
                                            obj, **where_dict)
            ConnectionManager.instance.conn.commit()
            return ret
        else:
            with closing(self._connection_manager.get_connection()) as conn:
                with conn as cursor:
                    return self.__update_not_closing(cursor, obj, **where_dict)

    def __update_not_closing(self, cursor, obj, **where_dict):
        parameters_values = [["=".join([i, "?"])
                              if _ == 0 else obj.__dict__[i]
                              for i in obj.__dict__.keys() if obj.__dict__[i]
                              is not None] for _ in range(2)]
        update_sql = "update " + type(obj).__name__ + " set "
        update_sql += ",".join(parameters_values[0])
        result_where = self.__create_where_clause(**where_dict)
        cursor.execute(update_sql + result_where[0],
                       tuple(parameters_values[1] + result_where[1]))
        return obj

    def insert(self, obj):
        """
        Parameters
        ----------
        obj : ?
           instance of the Type that represents the databse table
           that will be updated
        """

        if ConnectionManager.instance.in_memory:
            ret = self.__insert_not_closing(ConnectionManager.instance.conn,
                                            obj)
            ConnectionManager.instance.conn.commit()
            return ret
        else:
            with closing(self._connection_manager.get_connection()) as conn:
                with conn:
                    return self.__insert_not_closing(conn, obj)

    def __insert_not_closing(self, conn, obj):
        with closing(conn.cursor()) as cursor:
            param_dict = {k: v for k, v in obj.__dict__.items()
                          if v is not None}
            if len(param_dict) == 0:
                param_dict = {k: v for k, v in obj.__dict__.items()}
            insert_sql = ("insert into " + type(obj).__name__ + " (" +
                          ",".join(param_dict.keys()) + ") " +
                          "values(" +
                          ",".join("?" for _ in param_dict.values())) + ")"
            cursor.execute(insert_sql, tuple(param_dict.values()))
            return cursor.lastrowid

    def select(self, select_type, **where_dict):
        """
        Parameters
        ----------
        select_type : type
           Type that represents the databse table

        **where_dict :
           **kwargs parameter with the values to the where clause
        """

        if ConnectionManager.instance.in_memory:
            return self.__select_not_closing(ConnectionManager.instance.conn,
                                             select_type, **where_dict)
        else:
            with closing(self._connection_manager.get_connection()) as conn:
                with conn:
                    return self.__select_not_closing(conn, select_type,
                                                     **where_dict)

    def __select_not_closing(self, conn, select_type, **where_dict):
            conn.row_factory = sqlite3.Row
            with closing(conn.cursor()) as cursor:
                select_all_sql = "select "
                select_all_sql += ",".join(select_type().__dict__.keys())
                select_all_sql += " from " + select_type.__name__
                result_where = self.__create_where_clause(**where_dict)
                cursor.execute(select_all_sql + result_where[0],
                               tuple(result_where[1]))
                retorno = []
                for row in cursor.fetchall():
                    obj = select_type()
                    for k in obj.__dict__.keys():
                        setattr(obj, k, row[k])
                    retorno.append(obj)
                return retorno


class ConnectionManager(Singleton):
    """
    A class that defines methods to create a sqlite3 databse
    and/or clear it.

    Methods
    -------
    get_connection()
        returns the database connection
    """

    def __init__(self, data_base_location, entities_module_name, ddl_command,
                 in_memory=False, clear_data_base=False):
        """
        Parameters
        ----------
        data_base_location : str
           The database location

        entities_module_name : str
           The module name of the classes that represents the tables

        ddl_command : str
            The DDL commands to be executed on database's creation

        in_memory : bool
            Flag that indicates if the given database is in memory

        clear_data_base : bool
            Flag that indicates if the the clear database process should
            be executed
        """

        self._data_base_location = data_base_location
        self.in_memory = in_memory
        self.conn = None

        module_info = pyclbr.readmodule(entities_module_name)
        nomes_entidades = [i.name for i in module_info.values()
                           if i.name.lower().endswith('table')]

        if self.in_memory:
            self.conn = sqlite3.connect(self._data_base_location)
            self.__clear_database(self.conn, nomes_entidades, clear_data_base,
                                  ddl_command)
            self.conn.commit()
        else:
            with closing(self.get_connection()) as conn:
                with conn:
                    conn.row_factory = sqlite3.Row
                    self.__clear_database(conn, nomes_entidades,
                                          clear_data_base,
                                          ddl_command)

    def __clear_database(self, conn, nomes_entidades, clear_data_base,
                         ddl_command):
        with closing(conn.cursor()) as cursor:
            sql = "SELECT count(name) FROM sqlite_master WHERE name in (%s)"
            sql = sql % ",".join("?" * len(nomes_entidades))
            cursor.execute(sql, nomes_entidades)
            if cursor.fetchone()[0] != len(nomes_entidades):
                if clear_data_base:
                    for nome in nomes_entidades:
                        cursor.execute("DROP TABLE IF EXISTS %s" % nome)
                for create_sql in ddl_command.split(";"):
                    cursor.execute(create_sql)
        conn.commit()

    def get_connection(self):
        if self.in_memory:
            return self.conn
        else:
            return sqlite3.connect(self._data_base_location)
