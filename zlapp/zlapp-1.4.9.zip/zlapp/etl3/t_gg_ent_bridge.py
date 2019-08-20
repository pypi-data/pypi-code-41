import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta


def est1():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_ent_bridge 部分，先清空")
    sql="truncate etl.t_gg_ent_bridge"
    db_command(sql,dbtype="postgresql",conp=conp)
    bg=time.time()
    sql="""
    insert into etl.t_gg_ent_bridge
    with a as (SELECT html_key,href,ggtype,quyu
    ,zhongbiaoren as entname ,'中标人'::text entrole
    ,zhongbiaojia as price  
     FROM m1.n_gg  where zhongbiaoren is not null
     )
    ,b as (SELECT html_key,href,ggtype,quyu
    ,zhaobiaoren as entname ,'招标人'::text entrole
    ,kzj as price  
     FROM m1.n_gg  where zhaobiaoren is not null
     )
    ,c as (SELECT html_key,href,ggtype,quyu
    ,zbdl as entname ,'招标代理'::text entrole
    ,kzj as price  
     FROM m1.n_gg  where zbdl is not null
     )
    , d as (
     select * from a union  select * from b union select * from c)
    select d.*,t.diqu,t.xzqh,t.fabu_time,t.gg_name
     from d left join etl.gg_all  as t on d.html_key=t.html_key 
    """
    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()

    cost=int(ed-bg)
    print("耗时------%d秒"%cost)

def est2():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.t_gg_ent_bridge 
    SELECT html_key,    href,   ggtype, quyu,   zhongbiaoren as entname
    ,'中标人' as   entrole,zhongbiaojia     as price   ,NULL::text diqu
    ,   xzqh ,fabu_time, gg_name FROM "etl"."gg_zhongbiao" where quyu~'zlsys' 
    """
    db_command(sql,dbtype="postgresql",conp=conp)


def est():
    est1()
    est2()