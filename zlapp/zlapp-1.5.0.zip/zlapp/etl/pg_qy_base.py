import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC



def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.qy_base "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    select *,public.tydm_to_sh(tydm) as sh_info into public.qy_base from ent.t_base_est
    """
    db_command(sql,dbtype="postgresql",conp=conp)
