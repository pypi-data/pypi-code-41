import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


def est_bd_dt():
    sql="""
    create table public.bd_dt(
    html_key bigint ,
    guid text ,
    bd_key bigint,
    gg_name text ,
    ggtype text, 
    fabu_time timestamp, 
    gg_info text ,
    href text ,
    xzqh text ,
    create_time timestamp
    )
    distributed by (html_key)

    """
    conp=["gpadmin","since2015",'192.168.4.206','biaost',"public"]
    db_command(sql,dbtype="postgresql",conp=conp)


def update_bd_dt():


    sql="""
    insert into public.bd_dt(html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   , gg_info, href ,xzqh, create_time)
    select html_key,    guid,   bd_key  ,gg_name,   ggtype, fabu_time   ,info as gg_info,href ,xzqh,   create_time
    
    from public.gg  as a  where quyu~'^zlsys' 
    and not exists(select 1 from bd_dt as b  where  a.html_key=b.html_key)
    """
    print(sql)
    conp=["gpadmin","since2015",'192.168.4.206','biaost',"public"]
    db_command(sql,dbtype="postgresql",conp=conp)
