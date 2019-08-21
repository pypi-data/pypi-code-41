from SQLAlchemy_wrap.sql_factory import SqlalchemyFactory


class MysqlFactory(SqlalchemyFactory):

    # def db_connect(self, db_name, username, password, host="localhost", *args, **kw):
    #     sql_url = "mysql+pymysql://" + username + ":" + password + "@" + host + "/" + db_name
    #     super().connect(db_name, sql_url, *args, **kw)

    def db(self, db_name, username="", password="", host="127.0.0.1", *args, **kw):
        if username != "":
            sql_url = "mysql+pymysql://" + username + ":" + password + "@" + host + ":3306" + "/" + db_name
            super().connect(db_name, sql_url, *args, **kw)
        return super().db(db_name)
