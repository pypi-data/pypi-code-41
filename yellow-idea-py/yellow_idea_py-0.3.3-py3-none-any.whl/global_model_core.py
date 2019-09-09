import os
from yellow_idea_py.mysql import MySqlDatabase

db = MySqlDatabase(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    passwd=os.environ['DB_PASSWORD'],
    database=os.environ['DB_DATABASE']
)


class Register:

    @staticmethod
    def create(payload):
        return db.do_insert('master_register', payload)

    @staticmethod
    def edit(payload, user_id):
        where = f"id = '{user_id}'"
        return db.do_update('master_register', payload, where)

    @staticmethod
    def get_profile_by_line_id(line_user_id):
        query = f"SELECT * " \
                f"FROM view_register " \
                f"WHERE line_user_id = '{line_user_id}'"
        return db.do_obj(query)

    @staticmethod
    def report_register(where):
        query = 'SELECT a1.id,a2.line_display_image AS img_url,a2.line_display_name AS display_name,' \
                'a1.first_name AS name,a1.last_name,a1.phone_number,a1.address,' \
                'a1.updated_at FROM master_register AS a1 ' \
                'INNER JOIN master_user_line AS a2 ' \
                'ON a1.line_user_id=a2.id WHERE ' + where
        return db.do_list(query)

    @staticmethod
    def get_line_uuid(register_id):
        query = f"SELECT a2.line_user_id FROM master_register AS a1 INNER JOIN master_user_line AS a2 ON a1.line_user_id=a2.id WHERE a1.id='{register_id}'"
        return db.do_obj_key(query, 'line_user_id', None)

    @staticmethod
    def clear():
        where = f"id NOT IN ('0')"
        return db.do_delete("master_register", where)


class InitApp:

    @staticmethod
    def get_data(table):
        query = f"SELECT * FROM {table}"
        return db.do_list(query)
