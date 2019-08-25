import mysql.connector as mysql


class MySqlDatabase():

    def __init__(self, host, user, passwd, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database

    def connect(self):
        return mysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.database
        )

    def execute_commit(self, query):
        db = self.connect()
        sql = db.cursor()
        sql.execute(query)
        db.commit()
        result = sql.rowcount
        sql.close()
        return result

    def execute_fetch(self, query):
        db = self.connect()
        sql = db.cursor()
        sql.execute(query)
        columns = [col[0] for col in sql.description]
        rows = [dict(zip(columns, row)) for row in sql.fetchall()]
        sql.close()
        return rows

    def execute_store(self, store_name, params):
        db = self.connect()
        sql = db.cursor()
        sql.callproc(store_name, params)
        rows = []
        for result in sql.stored_results():
            columns = [col[0] for col in result.description]
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
        sql.close()
        return rows

    def genrate_query_insert(self, table, payload):
        str_builder = "INSERT INTO " + table + " ("
        value_builder = ""
        for index, key in enumerate(payload):
            if index == 0:
                str_builder += key
                value_builder += "'" + str(payload[key]) + "'"
            else:
                str_builder += ',' + key
                value_builder += ",'" + str(payload[key]) + "'"
        str_builder += ') VALUES (' + value_builder + ')'
        return str_builder

    def genrate_query_update(self, table, payload, where):
        str_builder = "UPDATE " + table + " SET "
        for index, key in enumerate(payload):
            if index == 0:
                str_builder += "%s = '%s'" % (key, str(payload[key]))
            else:
                str_builder += ",%s = '%s'" % (key, str(payload[key]))
        str_builder += ' WHERE ' + where
        return str_builder

    def do_store(self, store_name, params):
        try:
            result = self.execute_store(store_name, params)
            return result
        except mysql.Error as error:
            print("Store Fail", error, store_name)
            return []

    def do_fetch(self, query):
        try:
            result = self.execute_fetch(query)
            return result
        except mysql.Error:
            print("Fetch Fail", query)
            return []

    def do_insert(self, table, payload):
        query = self.genrate_query_insert(table, payload)
        try:
            result = self.execute_commit(query)
            if result > 0:
                print('Insert Success!')
                return True
            else:
                print("Insert Fail ", query)
                return False
        except mysql.Error:
            print("Insert Fail", query)
            return False

    def do_update(self, table, payload, where):
        query = self.genrate_query_update(table, payload, where)
        try:
            result = self.execute_commit(query)
            if result > 0:
                print('Update Success!', query)
                return True
            else:
                print("Update Fail", query)
                return False
        except mysql.Error as error:
            print("Update Fail", error, query)
            return False

    def do_delete(self, table, where):
        query = f"DELETE FROM {table} WHERE {where}"
        try:
            result = self.execute_commit(query)
            if result > 0:
                print('Delete Success!')
                return True
            else:
                print("Delete Fail", query)
                return False
        except mysql.Error:
            print("Delete Fail", query)
            return False
