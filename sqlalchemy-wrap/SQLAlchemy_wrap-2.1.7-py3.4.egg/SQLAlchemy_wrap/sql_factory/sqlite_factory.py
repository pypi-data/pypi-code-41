from SQLAlchemy_wrap.sql_factory import SqlalchemyFactory


class SqliteFactory(SqlalchemyFactory):

    def db(self, db_name, db_file=None, *args, **kw):
        if db_file is not None:
            # sqlite://<nohostname>/<path>
            sql_url = "sqlite:///" + db_file
            super().connect(db_name, sql_url, *args, **kw)
        return super().db(db_name)
