import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.bd_dt "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
select html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   ,info as gg_info,   create_time
into public.bd_dt
from cdc.t_gg_app where quyu='zlsys_yunnan_qujingshi' 
    """
    db_command(sql,dbtype="postgresql",conp=conp)
