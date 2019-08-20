import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.qy_zz "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    select *,public.entname_to_key(entname) as ent_key,substring(tydm,3,4) as xzqh
    , zzname_to_zzcode(zzmc) as zzcode,substring(zzmc,1,4) as alias into public.qy_zz
     from cdc.qyzz
    """
    db_command(sql,dbtype="postgresql",conp=conp)
