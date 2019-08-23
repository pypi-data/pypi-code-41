import _mssql
from c_mssql.mssql_sql import Sql_Mssql

class Mssql_Source(Sql_Mssql):
    def __init__(self,db_config):
        self.db_config=db_config

    def get_conn_title(self,data_conn):
        title_dict={}
        for rows in data_conn.get_header():
            title_dict[rows[0]]=self.pymssql_type_to_db_type(rows[1])
        return title_dict

    def get_sql_title(self,sql_str):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, database=self.db_config.database, port=self.db_config.port,charset='utf8')
        try:
            conn.execute_query(sql_str)
        except:
            raise(f"""sql运行出错{sql_str}""")

        title_dict=self.get_conn_title(conn)
        conn.close()
        return title_dict

    def get_conn(self,sql_str,with_title=False):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, database=self.db_config.database, port=self.db_config.port,charset='utf8')
        try:
            conn.execute_query(sql_str)
        except:
            raise(f"""sql运行出错{sql_str}""")
        if with_title:
            title_dict=self.get_conn_title(conn)
            return title_dict,conn
        else:
            return conn

    def get_datalist(self,sql_str,with_title=False):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, database=self.db_config.database, port=self.db_config.port,charset='utf8')
        try:
            conn.execute_query(sql_str)
        except:
            raise(f"""sql运行出错{sql_str}""")
        
        title_dict=self.get_conn_title(conn)
        data_list=[]
        for row in conn:
            row_dict={}
            for title in title_dict:
                row_dict[title]=row[title]
            data_list.append(row_dict)
        conn.close()
        if with_title:
            return title_dict,data_list
        else:
            return data_list


    def get_rowdict(self,sql_str):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, database=self.db_config.database, port=self.db_config.port,charset='utf8')
        row_dict=conn.execute_row(sql_str)
        conn.close()
        return row_dict

    def get_value(self,sql_str):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, database=self.db_config.database, port=self.db_config.port,charset='utf8')
        scalar=conn.execute_scalar(sql_str)
        conn.close()
        return scalar
