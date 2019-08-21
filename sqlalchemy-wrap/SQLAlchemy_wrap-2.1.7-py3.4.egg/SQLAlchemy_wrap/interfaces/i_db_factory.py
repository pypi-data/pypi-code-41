from abc import ABCMeta, abstractmethod
from .i_table import ITable


class IDbFactory(metaclass=ABCMeta):

    @abstractmethod
    def connect(self, database_name, **kw):
        """
            add a database connection, it will not set the instance's current db connect
        """
        pass

    @abstractmethod
    def db(self, database_name):
        """
            set the current db connection for instance, if database_name is not connected, it will attempt to
            connect
        :return: IDbFactory
        """
        pass

    @abstractmethod
    def close(self):
        """
            close current connection
        :return:
        """
        pass

    @abstractmethod
    def table(self, table_name: str) -> ITable:
        pass

    @abstractmethod
    def table_drop(self, table_name, database_name=None) -> bool:
        """
            drop the database if the database connection has establish, this is used for unittest
        :param table_name: the table name you want to drop
        :param database_name: the database name must be established and connected
        :return: bool
        """
        pass

    # @abstractmethod
    # def get_project(self) -> IProject:
    #     """
    #     :return: return class that operator project table
    #     """
    #     pass
