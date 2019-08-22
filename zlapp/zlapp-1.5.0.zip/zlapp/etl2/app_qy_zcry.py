import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def tb1():
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","public"]
    conp_pg=["postgres","since2015","192.168.4.188",'bid','cdc']
    sql="select * from etl.qyzcry"
    pg2pg(sql,'qyzcry',conp_hawq,conp_pg,chunksize=10000)


def est():
    tb1()
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.qy_zcry "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    SELECT 
    public.entname_to_key(entname) ent_key
     
    ,public.entname_to_tydm(entname) tydm

    ,substring(public.entname_to_tydm(entname),3,4) as  xzqh

    ,public.ryzz_to_code(zclb,zhuanye) as ryzz_code
    ,*
    ,public.ry_to_personkey(zjhm) as person_key
    into public.qy_zcry
     FROM "cdc"."qyzcry" 
    """
    db_command(sql,dbtype="postgresql",conp=conp)


