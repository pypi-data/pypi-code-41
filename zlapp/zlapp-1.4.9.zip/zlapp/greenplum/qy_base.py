import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC



def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.qy_base "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""
    select *,public.tydm_to_sh(tydm) as sh_info,substring(tydm,3,4) as xzqh into public.qy_base
    
     from ent.t_base_est
    """
    db_command(sql,dbtype="postgresql",conp=conp)




def est_qy_base():
    sql="""

    CREATE TABLE "public"."qy_base" (
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

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

def update_qybase():
    sql="""
    insert into public.qy_base(ent_key, jgmc,   tydm    ,zch,   jgdm    ,entid  ,clrq   ,jgdz,  fddbr,  jyfw,   jjhy    ,jglx,  zczj,   zczj_bz ,zczj_sj,   zczj_sj_bz, taxdm,  fromtime
    ,totime ,djbumen    ,jyzt,  engname,    bondnum,    zggm    ,email, phone   ,website    ,staff_info,    alias   
,diaoxiaodate   ,diaoxiaoreason ,zhuxiaodate    ,zhuxiaoreason  ,logo,  sh_info,    xzqh) 

    select ent_key, jgmc,   tydm    ,zch,   jgdm    ,entid  ,clrq   ,jgdz,  fddbr,  jyfw,   jjhy    ,jglx,  zczj,   zczj_bz ,zczj_sj,   zczj_sj_bz, taxdm,  fromtime
    ,totime ,djbumen    ,jyzt,  engname,    bondnum,    zggm    ,email, phone   ,website    ,staff_info,    alias   
,diaoxiaodate   ,diaoxiaoreason ,zhuxiaodate    ,zhuxiaoreason  ,logo,  sh_info::jsonb  sh_info,    xzqh from et_qy_base as a
    where not exists(select 1 from "public".qy_base  as b where a.ent_key=b.ent_key )
    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])