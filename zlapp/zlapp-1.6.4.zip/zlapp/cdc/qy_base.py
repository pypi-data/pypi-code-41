

# sql="select * from public.qy_base "

# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']

# pg2pg(sql,'qy_base',conp_app,conp_gp,chunksize=1000)

import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC




def est_qy_base():
    sql="""

    CREATE TABLE if not exists "etl"."qy_base" (
    "ent_key" bigint primary key ,
    "jgmc" varchar(500) ,
    "tydm" text ,
    "zch" text,
    "jgdm" text ,
    "entid" text ,
    "clrq" timestamp(6),
    "jgdz" text ,
    "fddbr" text ,
    "jyfw" text ,
    "jjhy" text ,
    "jglx" text ,
    "zczj" text ,
    "zczj_bz" text ,
    "zczj_sj" text ,
    "zczj_sj_bz" text ,
    "taxdm" text ,
    "fromtime" timestamp(6),
    "totime" timestamp(6),
    "djbumen" text ,
    "jyzt" text ,
    "engname" text ,
    "bondnum" text ,
    "zggm" text ,
    "email" text ,
    "phone" text ,
    "website" text ,
    "staff_info" text ,
    "alias" text ,
    "diaoxiaodate" text ,
    "diaoxiaoreason" text ,
    "zhuxiaodate" text ,
    "zhuxiaoreason" text ,
    "logo" text  ,
    "sh_info" jsonb,
    "xzqh" text 
    )
    distributed by (ent_key)"""

    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']

    db_command(sql,dbtype="postgresql",conp=conp)


def et_qy_base():
    sql="""
    drop external table if exists etl.et_qy_base;
    create  external table etl.et_qy_base(ent_key bigint,    jgmc text,  tydm text,  zch text,   jgdm text,  entid text, clrq  timestamp(6),
        jgdz text,  fddbr text ,    jyfw text   ,jjhy    text, jglx text,   zczj    text,
    zczj_bz text,   zczj_sj text,   zczj_sj_bz text,    taxdm    text, fromtime timestamp(6),    totime  timestamp(6) , djbumen text, jyzt   text,
    engname text,bondnum text,  zggm text,  email    text, phone text,  website  text,staff_info    text,
    alias text, diaoxiaodate text,  diaoxiaoreason   text,zhuxiaodate text, zhuxiaoreason text, logo text,  sh_info text,   xzqh  text  )
        LOCATION ('pxf://public.qy_base?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl'])


def update_qybase():
    est_qy_base()
    et_qy_base()
    sql="""
    truncate table etl.qy_base;
    insert into etl.qy_base(ent_key, jgmc,   tydm    ,zch,   jgdm    ,entid  ,clrq   ,jgdz,  fddbr,  jyfw,   jjhy    ,jglx,  zczj,   zczj_bz ,zczj_sj,   zczj_sj_bz, taxdm,  fromtime
    ,totime ,djbumen    ,jyzt,  engname,    bondnum,    zggm    ,email, phone   ,website    ,staff_info,    alias   
,diaoxiaodate   ,diaoxiaoreason ,zhuxiaodate    ,zhuxiaoreason  ,logo,  sh_info,    xzqh) 

    select ent_key, jgmc,   tydm    ,zch,   jgdm    ,entid  ,clrq   ,jgdz,  fddbr,  jyfw,   jjhy    ,jglx,  zczj,   zczj_bz ,zczj_sj,   zczj_sj_bz, taxdm,  fromtime
    ,totime ,djbumen    ,jyzt,  engname,    bondnum,    zggm    ,email, phone   ,website    ,staff_info,    alias   
,diaoxiaodate   ,diaoxiaoreason ,zhuxiaodate    ,zhuxiaoreason  ,logo,  sh_info::jsonb  sh_info,    xzqh from etl.et_qy_base as a

    """
    #    where not exists(select 1 from "public".qy_base  as b where a.ent_key=b.ent_key )
    print(sql)
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']

    db_command(sql,dbtype="postgresql",conp=conp)