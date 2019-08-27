from simple_sql_abs.dao import *
from simple_sql_abs.singleton import *

if __name__ == '__main__':

    class DumbTable:

        def __init__(self):
            self.id = None
            self.code = None

    DDLCOMMAND = """
                CREATE TABLE DumbTable (
                id INTEGER CONSTRAINT pk_role PRIMARY KEY AUTOINCREMENT,
                code INTEGER
                );
                """

    data_base_location = ':memory:'

    ConnectionManager(data_base_location, 'simple_sql_abs', DDLCOMMAND,
                      in_memory=True, clear_data_base=False)

    _dao = BaseDao()
    _dao.delete(DumbTable)

    t = DumbTable()
    t.code = 1

    _id = _dao.insert(t)
    select = _dao.select(DumbTable, id=_id)
    print(len(select))

    t2 = select[0]

    t2.code = 2
    _dao.update(t2, id=t2.id)
    select = _dao.select(DumbTable, id=_id)
    print(select[0].code)

    _dao.delete(DumbTable, id=_id)
    select = _dao.select(DumbTable, id=_id)
    print(len(select))
