import time, threading
from c_mssql.mssql_source import Mssql_Source
from c_mssql.mssql_execute import mssql_execute

lock = threading.Lock()
taskcount=0

class Mssql_Dst(Mssql_Source):
    """description of class"""
    def __init__(self,db_config,run_task=2):
        self.db_config=db_config
        self.run_task=run_task
        
    #行数据处理
    def row_process(self,dict_row):
        return dict_row

    #带锁的数据插入
    def run_import(self,dst_db,titleStr,sql_datastr_list):
        global taskcount
        taskcount+=1
        lock.acquire()
        try:
            #标题和数据行
            sql_str_data="Union All\n".join(sql_datastr_list)
            mssql_execute(dst_db,titleStr+"\n"+ sql_str_data)
        finally:
            lock.release()
            taskcount-=1
    
    def import_into_dst(self,data_conn,dst_table,dst_title=None,source_title=None,batch=1000):
 
        #如果目标表字段未给定
        if dst_title is None:
            sql_str=f"""select * from {dst_table} with(nolock) where 1=2"""
            dst_title=self.get_sql_title(sql_str)

        elif type(dst_title)==list:
            sql_str=f"""select {",".join(dst_title)} from {dst_table} with(nolock) where 1=2"""
            dst_title_temp=self.get_sql_title(sql_str)
            dst_title_dict={}
            for title in dst_title:
                dst_title_dict[title]=dst_title_temp[title]
            dst_title=dst_title_dict

        if source_title is None:
            source_title=dst_title

        elif type(source_title)==list:
            source_title_dict={}
            for title in source_title:
                if title in dst_title:
                    source_title_dict[title]=dst_title[title]
                else:
                    source_title_dict[title]="string"
            source_title=source_title_dict


        #插入数据的Insert头部语句
        title_str=self.get_insert_title_str(dst_table,dst_title)
        #待插入的数据
        sql_str_data_list=[]
        #行计数 
        rowcount=0
        global taskcount
        for row in data_conn:
            rowcount+=1
            dict_source_row={}
            #获取数据单行
            for title in source_title:
                dict_source_row[title]=row[title]
            #对每行数据进行处理
            dst_row_dict=self.row_process(dict_source_row)
            sql_str_data=self.get_select_row_str(dst_title, dst_row_dict)+"\n"
            sql_str_data_list.append(sql_str_data)
            if len(sql_str_data_list)==batch:
                while taskcount>self.run_task:
                    time.sleep(0.01)
                t1 = threading.Thread(target=self.run_import, args=(self.db_config,title_str,sql_str_data_list,))
                t1.start()
                sql_str_data_list=[]


        if len(sql_str_data_list)>0:
            t1 = threading.Thread(target=self.run_import, args=(self.db_config,title_str,sql_str_data_list,))
            t1.start()
        #等待任务结束
        while taskcount>0:
            time.sleep(0.01)
            pass
        return rowcount



