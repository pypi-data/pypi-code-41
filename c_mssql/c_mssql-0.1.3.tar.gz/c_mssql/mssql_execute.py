import _mssql
import os
from c_mssql.mssql_sql import Sql_Mssql

def error_log(str,file_name="error.txt"):
    if not os.path.exists("error.txt"):
        # send_message("etl_sql")
        # print("发送短信通知！")
        pass

    fo = open("error.txt", "w")
    fo.write( str)
    
    # 关闭打开的文件
    fo.close()

def mssql_execute(db_config,SQLStr):
    conn = _mssql.connect(server=db_config.server, user=db_config.user, password=db_config.password, port=db_config.port, database=db_config.database,charset='utf8')
    try:
        conn.execute_non_query(SQLStr)
    except:
        error_log(SQLStr)
    finally:
        conn.close()



class Mssql_Execute(Sql_Mssql):
    def __init__(self,db_config):
        self.db_config=db_config

    def mssql_execute(self,SQLStr):
        conn = _mssql.connect(server=self.db_config.server, user=self.db_config.user, password=self.db_config.password, port=self.db_config.port, database=self.db_config.database,charset='utf8')
        try:
            conn.execute_non_query(SQLStr)
        except:
            error_log(SQLStr) 
        finally:
            conn.close()

