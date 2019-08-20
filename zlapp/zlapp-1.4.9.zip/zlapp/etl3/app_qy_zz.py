import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def tb1():
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]
    conp_pg=["postgres","since2015","192.168.4.188",'bid','cdc']
    sql="select * from etl.qyzz"
    pg2pg(sql,'qyzz',conp_hawq,conp_pg,chunksize=10000)

def modf_xian():
    sql="""update public.qy_zz set zzmc=regexp_replace(zzmc,'[^\u4e00-\u9fa5a-zA-Z0-9]','','g')"""
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""update public.qy_zz set zzcode=zzname_to_zzcode(substring(zzmc,1,length(zzmc)-1))||'x' where zzmc~'限$' """
    db_command(sql,dbtype="postgresql",conp=conp)


def est():
    tb1()
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

    modf_xian()
