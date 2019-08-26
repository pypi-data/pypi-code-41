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

    sql="truncate table public.app_gg_zhongbiao"

    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""
    insert into public.app_gg_zhongbiao
    select a.*
    ,b.clrq,b.zczj,b.fddbr
    ,c.fabu_time[1] as lates_zhongbiaotime
    ,c.zhongbiao_counts
    
     from gg_zhongbiao  as a left join  qy_base as b on a.zhongbiaoren=b.jgmc
    left join qy_zhongbiao as c on a.zhongbiaoren=c.zhongbiaoren  

    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)


