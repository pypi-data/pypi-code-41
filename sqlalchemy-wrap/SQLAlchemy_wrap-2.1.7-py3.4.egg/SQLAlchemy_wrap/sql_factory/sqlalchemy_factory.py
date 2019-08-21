import sqlalchemy
from sqlalchemy import create_engine

from SQLAlchemy_wrap.exceptions import DbNotConnect
from SQLAlchemy_wrap.interfaces import IDbFactory
from .base_table import BaseTable


class DbEngine:
    def __init__(self, engine_name: str, engine):
        engine.connect()
        self._engine = engine
        self._tables = {}
        self._cur_table = None
        self._engine_name = engine_name

    def get_name(self):
        return self._engine_name

    def exists_table(self, table_name: str) -> bool:
        return table_name in self._tables.keys()

    def set_table(self, table_name, table_instance):
        self._tables[table_name] = table_instance

    def get_table(self, table_name):
        return self._tables[table_name]

    def get_cur_table(self):
        return self._cur_table

    def set_cur_table(self, table_name):
        self._cur_table = self._tables[table_name]

    def get_engine(self):
        return self._engine

    def close_engine(self):
        self.get_engine().dispose()


class SqlalchemyFactory(IDbFactory):
    # _tables = {}
    _connect = None
    _cur_engine = None
    # _cur_engine_name = None
    # _cur_col = None
    _db_dir = None

    # engine = None

    def __init__(self, db_dir: str = None):
        '''
            assign database dir that contain table operator class
        :param db_dir: if db_dir is None, table('table_name') will return BaseTable(), if it's "", it will find in
                       current dir, otherwise find in db_dir

        '''
        self._db_dir = db_dir
        self._db_engines = {}

    def connect(self, db_name, *args, **kw):
        """
            add a database connection, it will not set the instance's current db connect
        """
        engine = create_engine(*args, **kw)
        self._db_engines[db_name] = DbEngine(db_name, engine)
        self._cur_engine = self._db_engines[db_name]

    def db(self, db_name):
        """
            set the current db connection for instance, if database_name is not connected, it will attempt to
            connect
        :return: IDbFactory
        """
        if db_name in self._db_engines:
            self._cur_engine = self._db_engines[db_name]
            self._cur_engine_name = db_name
            return self
        else:
            raise DbNotConnect("database '" + db_name + "' is not connect, you can use connect() to connect db")

    def table(self, table_name: str):
        if not self._cur_engine.exists_table(table_name):
            table_instance = self._get_table_operate_class(self._cur_engine.get_name(), table_name)
            self._cur_engine.set_table(table_name, table_instance)
            self._cur_engine.set_cur_table(table_name)

        return self._cur_engine.get_cur_table()

    def _get_table_operate_class(self, db_name: str, table_name: str):
        try:
            if self._db_dir is None:
                return self.get_base_table_instance(table_name, db_name)
                # return BaseTable(self._cur_engine.get_engine(), table_name)
            elif self._db_dir == "":
                __import__(db_name)
            else:
                __import__(self._db_dir + "." + db_name)

            m = __import__(self._db_dir + "." + db_name, fromlist=[table_name])
            for attr_name in dir(m):
                if table_name == attr_name:
                    if type(getattr(m, attr_name)) == type and \
                            issubclass(getattr(m, attr_name), BaseTable):
                        table_name = attr_name
                        break
            cls = getattr(m, table_name)
            return cls(self._cur_engine.get_engine())
        # todo: handle exception
        #   暂时如果没找到对应类, 就使用BaseTable()生成一个基本类
        #   如果没存在对应表,是会抛出异常的
        # except ModuleNotFoundError as e:
        #     base_table = BaseTable(self._cur_engine, table_name)
        #     return base_table
        # except AttributeError as e:
        #     base_table = BaseTable(self._cur_engine, table_name)
        #     return base_table
        except Exception as e:
            return self.get_base_table_instance(table_name, db_name)

    def table_drop(self, table_name, database_name=None):
        pass

    def get_base_table_instance(self, table_name: str, db_name: str) -> BaseTable:
        msg = "{}.{} not exists table operator class `{}`, return BaseTable()" \
            .format(self._db_dir, db_name, table_name)
        print(msg)
        return BaseTable(self._cur_engine.get_engine(), table_name)

    def close(self):
        if self._cur_engine:
            self._cur_engine.close_engine()
            self._db_engines.pop(self._cur_engine.get_name())
            self._cur_engine = None

    def exec(self, *args, **kw) -> sqlalchemy.engine.result.ResultProxy:
        """
           execute sql in current db connect
        """
        return self._cur_engine.execute(*args, **kw)

    def get_cur_engine(self):
        return self._cur_engine

    def __del__(self):
        self._db_engines.clear()
        # self._tables.clear()
