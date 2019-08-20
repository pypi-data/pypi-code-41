import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est1():

    sql="select * from etl.gg_zhongbiao "
    tbname="gg_zhongbiao"
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    bg=time.time()
    datadict={"html_key":BIGINT(),"gg_name":TEXT(),"href":TEXT(),"fabu_time":TIMESTAMP(),"ggtype":TEXT(),"zhongbiaojia":NUMERIC(),"kzj":NUMERIC(),"xzqh":TEXT()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=100000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)


def est2():
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]

    sql="truncate table public.gg_zhongbiao"

    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""
    insert into public.gg_zhongbiao( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,   xmdz ,
       zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key)
    select html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,   xmdz ,
       zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title::tsvector ts_title 
        ,public.entname_to_key(zhongbiaoren) as ent_key 

        from cdc.gg_zhongbiao 
        """
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def est():
    est1()
    est2()
