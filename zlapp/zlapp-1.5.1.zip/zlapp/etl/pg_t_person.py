import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="""
insert into  "public"."t_person"(name,zj_type,zjhm)


select distinct on(name,zjhm) name,zj_type,zjhm from cdc.qyzcry  as b 

where zjhm is not null and  not exists(select 1 from public.t_person as a where a.zjhm=b.zjhm)
    """
    db_command(sql,dbtype="postgresql",conp=conp)