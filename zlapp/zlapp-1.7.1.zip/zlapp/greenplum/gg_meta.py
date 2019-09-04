import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time

def est_gg_meta():
    sql="""
    CREATE TABLE if not exists "public"."gg_meta" (
    "html_key" bigint NOT NULL,
    "guid" text COLLATE "default",
    "gg_name" text COLLATE "default",
    "href" text COLLATE "default",
    "fabu_time" timestamp(6),
    "ggtype" text COLLATE "default",
    "jytype" text COLLATE "default",
    "diqu" text COLLATE "default",
    "quyu" text COLLATE "default",
    "info" text COLLATE "default",
    "create_time" timestamp(6),
    "xzqh" text COLLATE "default",
    "ts_title" tsvector,
    "bd_key" int8,
    "person" text COLLATE "default",
    "price" numeric,

    zhaobiaoren text ,
    zhongbiaoren    text,
    zbdl text , 
    zhongbiaojia text   ,
    kzj float ,
    xmmc text , 
    xmjl text , 
    xmjl_zsbh text  ,
    xmdz text ,
    zbfs text ,
    xmbh text , 
    mine_info text 
    ) distributed by(html_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_gg_meta():
    bg=time.time()
    est_gg_meta()
    sql="""truncate public.gg_meta;"""
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])
    sql="""
    
    insert into "public".gg_meta(html_key,  guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   ,create_time,   xzqh,   ts_title    ,bd_key ,person ,price
    ,zhaobiaoren    ,zhongbiaoren   ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh, xmdz,   zbfs    ,xmbh,  mine_info) 

    select html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   
    ,create_time,   xzqh,   ts_title::tsvector as ts_title  ,bd_key ,person ,price::numeric as price
    ,zhaobiaoren    ,zhongbiaoren   ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh, xmdz,   zbfs    ,xmbh,  mine_info
     from et_gg_meta as a
    
    """
    #where not exists(select 1 from gg_meta  as b where a.html_key=b.html_key ) and fabu_time>='1900-01-01' and fabu_time<'2019-12-31'
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

    ed=time.time()
    cost=int(ed-bg)
    print("gg_meta 全表重导入耗时%s 秒"%cost)