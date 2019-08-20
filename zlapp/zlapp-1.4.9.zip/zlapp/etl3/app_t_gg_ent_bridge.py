import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est1():

    sql="select * from etl.t_gg_ent_bridge"
    tbname="t_gg_ent_bridge"
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    bg=time.time()
    datadict={"html_key":BIGINT(),"price":NUMERIC(),"xzqh":TEXT()}
    def f(df):
        df['fabu_time']=df['fabu_time'].map(lambda x:x if str(x)<'2050-01-01' and str(x)>'1900-01-01' else '2050-01-01')
        return df 
    pg2pg(sql,tbname,conp_hawq,conp_pg,f=f,chunksize=10000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)


def est2():
    conp=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    sql="""drop table if exists public.t_gg_ent_bridge"""
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    SELECT *,public.entname_to_key(entname) as ent_key 
    into public.t_gg_ent_bridge
     FROM "cdc"."t_gg_ent_bridge";
     """
    db_command(sql,dbtype="postgresql",conp=conp)



def est():
    est1()
    est2()
    