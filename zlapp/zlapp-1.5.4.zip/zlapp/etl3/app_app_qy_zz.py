import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est():
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"public"]
    sql="""

    drop table if exists public.app_qy_zz;
    with a as (SELECT  ent_key, entname,zzlb,zzmc,zzbh,zzcode,xzqh,fddbr,alias  FROM "public"."qy_zz" where ent_key is not null )
    ,b as (select jgmc,clrq,zczj,logo,alias as qy_alias from public.qy_base)

    ,c as (select zhongbiaoren,gg_fabutimes[1] as fabu_time,zhongbiao_counts from public.qy_zhongbiao )

    select 
    a.*,b.clrq,b.zczj,b.logo,b.qy_alias
    ,coalesce(c.fabu_time,'1900-01-01'::timestamp(0)) as fabu_time
    ,coalesce(c.zhongbiao_counts,0) as total 

    into public.app_qy_zz
    from a left join b on a.entname=b.jgmc left join c  on a.entname=c.zhongbiaoren  
    ;

    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)