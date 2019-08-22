import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est2():
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]

    sql="truncate table public.qy_zhongbiao"

    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""
    insert into public.qy_zhongbiao
    with a as (SELECT zhongbiaoren
    ,array_agg(gg_name order by fabu_time desc ) as gg_names 


    ,array_agg(fabu_time order by fabu_time desc) gg_fabutimes

    ,array_agg(html_key order by fabu_time desc) html_keys

    ,array_agg(zhongbiaojia order by fabu_time desc ) as zhongbiaojias 
    ,count(*) zhongbiao_counts



     FROM "public"."gg_zhongbiao" group by zhongbiaoren )


    select *,public.entname_to_key(zhongbiaoren) as ent_key

     from a 
    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)


