import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est():
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    sql="""

    drop table if exists public.app_qy_zcry;
    SELECT 
    a.*

    ,b.zhongbiao_counts as total 
    ,b.gg_fabutimes[1] as fabu_time 
    
    ,d.zczj
    ,d.fddbr
    ,d.clrq
    ,d.alias as qy_alias
    ,public.entkey_to_logo(a.ent_key) as logo
    into public.app_qy_zcry
    FROM "public"."qy_zcry" as a left join public.qy_zhongbiao as b
    on a.entname=b.zhongbiaoren
    left join t_person as c on a.name=c.name and a.zjhm=c.zjhm
    left join public.qy_base as d on a.entname=d.jgmc
     ;

    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)