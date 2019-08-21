from sql_factory.base_table import BaseTable


class UseExistsTable(BaseTable):
    __tablename__ = "UnittestTable"

    def insert_by_id(self, id: int, content: dict):
        if "id" not in content.keys():
            content["id"] = id
        self.insert(content)
