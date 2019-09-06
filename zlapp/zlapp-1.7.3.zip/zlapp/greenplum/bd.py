import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC






def est_bd():
    sql="""
    CREATE TABLE if not exists "public"."bd" (
    "bd_key" int8,
    "bd_guid" text COLLATE "default",
    "bd_name" text COLLATE "default",
    "bd_bh" text COLLATE "default",
    "zhaobiaoren" text COLLATE "default",
    "zbdl" text COLLATE "default",
    "kzj" numeric,
    "xm_name" text COLLATE "default",
    "fabu_time" timestamp(6),
    "quyu" text COLLATE "default",
    "xzqh" text COLLATE "default"
    )
    distributed by (bd_key)

    """

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

def update_bd():
    est_bd()
    conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    sql="""    truncate table "public".bd;"""
    db_command(sql,dbtype="postgresql",conp=conp_app)

    sql="""

    insert into "public".qy_zz(href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias)
    SELECT href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias   FROM "public"."et_qy_zz";
        """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=conp_app)