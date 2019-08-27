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
    sql="""drop table if exists public.t_bd_xflv;"""
    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""

    with   a as (select 
    bd_key
    ,(array_agg(info::jsonb->>'zbr'))[1] as zbr
    ,(array_agg(info::jsonb->>'zhongbiao_hxr'))[1] as zhongbiaoren
    ,(array_agg(info::jsonb->>'kzj'))[1] as kzj
    ,(array_agg(info::jsonb->>'zhongbiaojia'))[1] as zhongbiaojia
    ,(array_agg(info::jsonb->>'bd_bh'))[1] as bd_bh

    ,(array_agg(xzqh))[1] as xzqh
    ,array_to_json(array_agg(json_build_object('html_key',html_key,'ggtype',ggtype,'gg_name',gg_name,'fabu_time',fabu_time) order by fabu_time desc) ) as gg_info
    ,(array_agg(fabu_time order by fabu_time asc)  )[1] zhaobiao_time
    ,(array_agg(fabu_time order by fabu_time desc) )[1] zhongbiao_time


     from public.gg where quyu~'zlsys'  
    group by bd_key )

    ,b as(

    select *,  1-(zhongbiaojia::float)/(kzj::float) as xflv from a where kzj is not null and kzj::float>0 and zhongbiaojia is not null )

    select bd_key   ,zbr,zhaobiao_time,zhongbiao_time,  zhongbiaoren,   kzj::float kzj  ,
    zhongbiaojia::float zhongbiaojia,   bd_bh,  xzqh,   gg_info,  case when round(xflv::numeric,4)<0 then 0 else round(xflv::numeric,4) end as xflv 
    into public.t_bd_xflv
    from b

    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)