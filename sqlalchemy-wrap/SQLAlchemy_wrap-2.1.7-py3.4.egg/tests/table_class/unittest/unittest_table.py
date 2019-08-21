from sqlalchemy import Column, String, Integer

from sql_factory.base_table import BaseTable


class UnittestTable(BaseTable):
    table_columns = [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(50)),
        Column('obj', String)
    ]

    def insert_by_id(self, id: int, content: dict):
        if "id" not in content.keys():
            content["id"] = id
        self.insert(content)
