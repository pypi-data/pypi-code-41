import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC






def est_qy_zcry():
    sql="""
    CREATE TABLE if not exists "etl"."qy_zcry" (
    "ent_key" int8,
    "tydm" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "ryzz_code" text COLLATE "default",
    "href" text COLLATE "default",
    "name" text COLLATE "default",
    "gender" text COLLATE "default",
    "zjhm" text COLLATE "default",
    "zj_type" text COLLATE "default",
    "zclb" text COLLATE "default",
    "zhuanye" text COLLATE "default",
    "zsbh" text COLLATE "default",
    "yzh" text COLLATE "default",
    "youxiao_date" text COLLATE "default",
    "entname" text COLLATE "default",
    "person_key" int8
    ) distributed by (person_key)

    """

    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']

    db_command(sql,dbtype="postgresql",conp=conp)

def et_qy_zcry():
    sql="""
        drop external table if exists etl.et_qy_zcry;
    create  external table etl.et_qy_zcry(ent_key bigint,    tydm text,  xzqh text,  ryzz_code text,
    href text,  name    text ,gender text,  zjhm text,  zj_type text,   zclb text,  zhuanye  text, zsbh text,   yzh  text ,youxiao_date text,   entname text, person_key bigint  )
        LOCATION ('pxf://public.qy_zcry?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015&PARTITION_BY=person_key:int&RANGE=1:5000000&INTERVAL=10000')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']
    db_command(sql,dbtype="postgresql",conp=conp)


def update_qy_zcry():
    et_qy_zcry()
    est_qy_zcry()
    sql="""
    truncate table etl.qy_zcry;
    insert into etl.qy_zcry(ent_key  ,tydm   ,xzqh,  ryzz_code,  href,   name    ,gender ,zjhm,  zj_type,    zclb,   zhuanye ,zsbh   ,yzh    ,youxiao_date,  entname,    person_key) 

    select ent_key  ,tydm   ,xzqh,  ryzz_code,  href,   name    ,gender ,zjhm,  zj_type,    zclb,   zhuanye ,zsbh   ,yzh    ,youxiao_date,  entname,    person_key from etl.et_qy_zcry as a
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']

    db_command(sql,dbtype="postgresql",conp=conp)