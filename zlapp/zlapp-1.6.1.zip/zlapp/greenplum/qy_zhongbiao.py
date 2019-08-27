import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 
def est_qy_zhongbiao():
    sql="""
    CREATE TABLE if not exists "public"."qy_zhongbiao" (
    "zhongbiaoren" text COLLATE "default",
    "gg_names" _text,
    "gg_fabutimes" _timestamp,
    "html_keys" _int8,
    "zhongbiaojias" _numeric,
    "zhongbiao_counts" int8,
    "ent_key" int8
    ) distributed by (ent_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_qy_zhongbiao():
    bg=time.time()
    est_qy_zhongbiao()
    sql="""    truncate  public.qy_zhongbiao;"""
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])
    sql="""
    insert into public.qy_zhongbiao(zhongbiaoren,   gg_names,   gg_fabutimes,   html_keys,  zhongbiaojias,  zhongbiao_counts,   ent_key)


    with a as (SELECT zhongbiaoren
    ,array_agg(gg_name order by fabu_time desc ) as gg_names 


    ,array_agg(fabu_time order by fabu_time desc) gg_fabutimes

    ,array_agg(html_key order by fabu_time desc) html_keys

    ,array_agg(zhongbiaojia order by fabu_time desc ) as zhongbiaojias 
    
    ,count(*) zhongbiao_counts
    
    ,(array_agg(ent_key order by fabu_time desc ))[1] as ent_key 


     FROM "public"."gg_zhongbiao" group by zhongbiaoren )


    select * from a 

 
    """
    #select a.*,b.ent_key from a left join  "public".qy_base  as b on a.zhongbiaoren=b.jgmc 
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

    ed=time.time()
    cost=int(ed-bg)
    print("qy_zhongbiao表更新需要 %s "%cost)