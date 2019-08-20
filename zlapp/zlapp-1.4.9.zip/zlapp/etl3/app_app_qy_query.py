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

    sql1="""    drop table if exists public.app_qy_query;"""
    db_command(sql1,dbtype="postgresql",conp=conp_pg)
    
    sql="""
    with a as (SELECT ent_key,jgmc as entname,fddbr,clrq,zczj,xzqh,alias as qy_alias FROM "public"."qy_base" )

    ,b as (select ent_key,gg_fabutimes[1] as zhongbiaodate_latest,zhongbiao_counts from public.qy_zhongbiao where ent_key is not null  )

    ,c as (SELECT ent_key, array_agg(zzmc) as qy_zz_info,string_agg('code-'||zzcode,',') as qy_zz_codes

     FROM "public"."qy_zz" where ent_key is not null group by ent_key)

    ,d as (
    select ent_key
    , array_agg(json_build_object( 'person_name',name,'person_key',person_key,'zzmc',concat(zclb,'-',zhuanye)
    ,'currentTotal','','currentDate','' ) order by youxiao_date,name ) as ry_zz_info
    ,string_agg('code-'||ryzz_code,',') ry_zz_codes
     from public.qy_zcry where ent_key is not null 

    group by ent_key 
    )

    ,e as (
    SELECT 
    ent_key, 
    array_agg(json_build_object('html_key',html_key,'gg_name',gg_name,'gg_type',ggtype,'fabu_time',fabu_time) order by fabu_time desc ,gg_name) gg_info

     FROM "public"."t_gg_ent_bridge" 
    where ent_key is not null

    group by ent_key)

    select a.* ,b.zhongbiaodate_latest,b.zhongbiao_counts 
    ,c.qy_zz_codes
    ,c.qy_zz_info
    ,d.ry_zz_codes
    ,d.ry_zz_info
    ,e.gg_info 

    into public.app_qy_query
    from a left join b on a.ent_key=b.ent_key 
    left join c on a.ent_key=c.ent_key 
    left join d on a.ent_key=d.ent_key 
    left join e on a.ent_key=e.ent_key 
    """
    db_command(sql,dbtype="postgresql",conp=conp_pg)