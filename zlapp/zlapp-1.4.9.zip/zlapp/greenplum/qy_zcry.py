import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC






def est_qy_zcry():
    sql="""
    CREATE TABLE "public"."qy_zcry" (
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

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

def update_qy_zcry():
    sql="""
    insert into public.qy_zcry(ent_key  ,tydm   ,xzqh,  ryzz_code,  href,   name    ,gender ,zjhm,  zj_type,    zclb,   zhuanye ,zsbh   ,yzh    ,youxiao_date,  entname,    person_key) 

    select ent_key  ,tydm   ,xzqh,  ryzz_code,  href,   name    ,gender ,zjhm,  zj_type,    zclb,   zhuanye ,zsbh   ,yzh    ,youxiao_date,  entname,    person_key from et_qy_zcry as a
    where not exists(select 1 from "public".qy_zcry  as b where a.ent_key=b.ent_key and a.ryzz_code=b.ryzz_code and a.ryzz_code is not null  )
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])