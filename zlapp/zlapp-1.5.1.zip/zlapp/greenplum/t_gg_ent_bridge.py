import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_t_gg_ent_bridge():
    sql="""
    CREATE TABLE "public"."t_gg_ent_bridge" (
    "html_key" int8 ,
    "href" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "quyu" text COLLATE "default",
    "entname" text COLLATE "default",
    "entrole" text COLLATE "default",
    "price" numeric,
    "diqu" text COLLATE "default",
    "xzqh" text COLLATE "default",
    "fabu_time" timestamp(6),
    "gg_name" text COLLATE "default",
    "ent_key" int8
    )
    distributed by (html_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])


def update_t_gg_ent_bridge():
    sql="""
    truncate public.t_gg_ent_bridge;
    insert into t_gg_ent_bridge(html_key,   href    ,ggtype ,quyu,  entname ,entrole,   price   ,diqu,  xzqh,   fabu_time,  gg_name,    ent_key)
        with a as (SELECT html_key,href,ggtype,quyu
        ,zhongbiaoren as entname ,'中标人'::text entrole
        ,zhongbiaojia::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM "public".gg_meta  where zhongbiaoren is not null
         )
        ,b as (SELECT html_key,href,ggtype,quyu
        ,zhaobiaoren as entname ,'招标人'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM "public".gg_meta where zhaobiaoren is not null
         )
        ,c as (SELECT html_key,href,ggtype,quyu
        ,zbdl as entname ,'招标代理'::text entrole
        ,kzj::float as price  ,diqu,xzqh,fabu_time,gg_name
         FROM "public".gg_meta  where zbdl is not null
         )
        , d as (
         select * from a union  select * from b union select * from c)
    select distinct on(html_key,entname,entrole) d.*,ent_key from d  left join public.qy_base as e  on d.entname=e.jgmc 
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])