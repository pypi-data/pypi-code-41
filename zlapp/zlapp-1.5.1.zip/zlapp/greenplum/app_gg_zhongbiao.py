import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est_app_gg_zhongbiao():
    sql="""
    CREATE TABLE "public"."app_gg_zhongbiao" (
    "html_key" int8,
    "href" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "quyu" text COLLATE "default",
    "zhongbiaoren" text COLLATE "default",
    "zhaobiaoren" text COLLATE "default",
    "zbdl" text COLLATE "default",
    "zhongbiaojia" numeric,
    "kzj" numeric,
    "xmmc" text COLLATE "default",
    "xmjl" text COLLATE "default",
    "xmdz" text COLLATE "default",
    "zbfs" text COLLATE "default",
    "xmbh" text COLLATE "default",
    "gg_name" text COLLATE "default",
    "fabu_time" timestamp(6),
    "xzqh" text COLLATE "default",
    "ts_title" tsvector,
    "ent_key" int8,
    "clrq" timestamp(6),
    "zczj" text COLLATE "default",
    "fddbr" text COLLATE "default",
    "lates_zhongbiaotime" timestamp(6),
    "zhongbiao_counts" int8
    )

    distributed by(html_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_app_gg_zhongbiao():
    sql="""
    truncate public.app_gg_zhongbiao;
    insert  into public.app_gg_zhongbiao(html_key   ,href,  ggtype, quyu    ,zhongbiaoren   ,zhaobiaoren,   zbdl,   zhongbiaojia    ,kzj    ,xmmc,xmjl,
    xmdz,zbfs,xmbh,gg_name,fabu_time,xzqh   
    ,ts_title,ent_key,clrq,zczj,fddbr,lates_zhongbiaotime,zhongbiao_counts)
    select a.*
    ,b.clrq,b.zczj,b.fddbr
    ,c.gg_fabutimes[1] as lates_zhongbiaotime
    ,c.zhongbiao_counts

     from public.gg_zhongbiao  as a left join  "public".qy_base as b on a.zhongbiaoren=b.jgmc
    left join public.qy_zhongbiao as c on a.zhongbiaoren=c.zhongbiaoren  

    """
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])