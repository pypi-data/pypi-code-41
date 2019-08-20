import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_app_qy_zcry():
    sql="""
    CREATE TABLE "public"."app_qy_zcry" (
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
    "person_key" int8,
    "total" int8,
    "fabu_time" timestamp(6),
    "zczj" text COLLATE "default",
    "fddbr" text COLLATE "default",
    "clrq" timestamp(6),
    "qy_alias" text COLLATE "default",
    "logo" text COLLATE "default"
    )
    distributed by (person_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_app_qy_zcry():
    sql="""
    truncate public.app_qy_zcry;
    insert into "public".app_qy_zcry(ent_key,   tydm,   xzqh    ,ryzz_code  ,href,  name,   gender  ,zjhm   ,zj_type,   zclb    ,zhuanye,   zsbh    ,yzh,   youxiao_date,   entname
        ,person_key ,total  ,fabu_time  ,zczj   
    ,fddbr  ,clrq   ,qy_alias   ,logo)
    SELECT 
    a.*

    ,b.zhongbiao_counts as total 
    ,b.gg_fabutimes[1] as fabu_time 

    ,d.zczj
    ,d.fddbr
    ,d.clrq
    ,a1.alias as qy_alias
    ,a1.logo
    FROM "public"."qy_zcry" as a left join "public".qy_base as a1
    on a.ent_key=a1.ent_key 
    left join public.qy_zhongbiao as b
    on a.entname=b.zhongbiaoren
    left join t_person as c on a.name=c.name and a.zjhm=c.zjhm
    left join public.qy_base as d on a.entname=d.jgmc
     ;
        """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])