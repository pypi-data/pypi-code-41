
class SQLBackend:
    def __init__(self, table_name, table_columns, table_ddl="", create_table=False):
        self.table_name = table_name
        self.columns = table_columns

        if create_table:
            self.create_table_if_not_exists(self.table_name, table_ddl)

    def consume(self, messages):
        data = ((msg.get(k, "") for k in self.columns) for msg in messages)
        self.copy(data)

    def copy(self, rows, delimiter=",", quote='"'):
        raise Exception("Implement this on subclasses!")

    def create_table_if_not_exists(self, tablename, table_definition, table_indexes=""):
        raise Exception("Implement this on subclasses!")
