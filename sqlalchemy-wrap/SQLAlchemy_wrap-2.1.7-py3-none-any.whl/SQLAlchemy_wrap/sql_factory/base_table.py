import typing

from sqlalchemy import *


class BaseTable():
    __tablename__ = None
    table_columns = None

    engine = None
    metadata = None
    connect = None

    table_cmd = None
    is_base_table = False

    @property
    def c(self):
        return self.connect.c

    def __init__(self, engine: create_engine, table_name=None):
        if self.__tablename__ is None:
            if table_name is not None:
                self.__tablename__ = table_name
            else:
                self.__tablename__ = self.__class__.__name__
        self.engine = engine
        self.metadata = MetaData(engine)

        # 不定义self.table_columns就从已有表加载
        # 否则创建表(如果不存在)并加载
        if self.table_columns is not None and len(self.table_columns) > 0:
            self.create_table_using_columns(*self.table_columns)
        else:
            try:
                self.connect = Table(self.__tablename__, self.metadata, autoload=True)
                self.metadata.create_all()
            except AttributeError as e:
                raise Exception("database don't exists table `{}`: {}".format(self.__tablename__, str(e)))

    def create_table_using_columns(self, *args):
        try:
            self.connect = Table(self.__tablename__, self.metadata, *args)
            self.metadata.create_all()
        except BaseException as e:  # pragma: no cover
            raise Exception("Create table `{}` failed: {}".format(self.__tablename__, str(e)))

    def update(self, update_content, where_clause: str = None, **kwargs):
        stmt = self.connect.update().values(update_content)
        if where_clause:
            where_clause = text(where_clause)
            print(where_clause)
            if len(kwargs):
                where_clause = where_clause.params(kwargs)
            stmt = stmt.where(where_clause)
        res = self.engine.execute(stmt)
        return res.rowcount

    def insert(self, document: dict):
        if document == {}:
            return
        self.engine.execute(self.connect.insert(), document)

    def insert_one(self, row_data_dict: dict):
        if isinstance(row_data_dict, dict):
            if len(row_data_dict) == 0:
                return
            self.insert_multi([row_data_dict])
        else:
            raise Exception("insert_one() parameter 1 must be dict")

    def insert_multi(self, rows_data_list: list):
        if isinstance(rows_data_list, list):
            if len(rows_data_list) == 0:
                return
            self.engine.execute(self.connect.insert(), rows_data_list)

        else:
            raise Exception("insert_multi() parameter 1 must be list")

    def exec_sql(self, sql, **kwargs):
        sql = text(sql)
        if len(kwargs) > 0:
            sql = sql.bindparams(kwargs)
        return self.engine.execute(sql)

    def remove(self, where_clause: str = None, **kwargs) -> int:
        '''
            remove records that mach condition
        :param condition: if it's None, remove all record
        :return: None
        '''
        # if condition is None:
        #     d = self.connect.delete()
        # else:
        #     d = self.connect.delete()
        #     for k in condition:
        #         d = d.where(getattr(self.connect.c, k) == condition[k])
        # self.engine.execute(d)
        from sqlalchemy import delete
        stmt = delete(self.connect)
        if where_clause:
            stmt = stmt.where(text(where_clause))
            if len(kwargs) > 0:
                stmt.params(kwargs)
        res = self.engine.execute(stmt)
        return res.rowcount

    def get(self, where_clause: str = None, **kwargs) -> typing.List[dict]:
        stmt = select([self.connect])
        if where_clause:
            stmt = stmt.where(text(where_clause))
            if len(kwargs):
                stmt.params(kwargs)
        res = self.engine.execute(stmt).fetchall()
        return self.sql_res_to_list_dict(res)

    def count(self) -> int:
        return \
            self.engine.execute(
                select(
                    [func.count()]
                ).select_from(
                    self.connect)
            ).fetchone()[0]

    def get_all(self) -> typing.List[dict]:
        return self.get()

    def get_connect(self):
        return self.connect

    def get_engine(self):
        return self.engine

    def sql_res_to_list_dict(self, res, col_name_list=None):
        if col_name_list is None:
            col_name_list = self.connect.columns.keys()
        if not isinstance(col_name_list, list):  # pragma: no cover
            col_name_list = [col_name_list]
        if res:
            record_list = []
            for e in res:
                d = dict(zip(col_name_list, e))
                record_list.append(d)
            return record_list
        else:
            return []

    def close(self):
        self.connect.close()
