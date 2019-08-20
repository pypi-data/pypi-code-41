import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC,TSVECTOR

from zlapp.etl2 import gg 

def gg_all(conp_pg):
    sql="select * from etl.gg_all  "
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    datadict={"html_key":BIGINT(),
    "price":NUMERIC(),'bd_key':BIGINT(),'fa_butime':TIMESTAMP(),'create_time':TIMESTAMP(),'ts_tile':TSVECTOR()}
    def f(df):
        df['fabu_time']=df['fabu_time'].map(lambda x:x if str(x)<'2050-01-01' and str(x)>'1900-01-01' else '2050-01-01')
        return df 
    pg2pg(sql,'gg',conp_hawq,conp_pg,f=f,chunksize=10000,datadict=datadict)


def gg_pk(conp_pg):
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="drop index if exists pk_gg_html_key;alter table public.gg add constraint pk_gg_html_key primary key(html_key) "
    db_command(sql,dbtype="postgresql",conp=conp_pg)

def gg_ts(conp_pg):
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="""alter table "public"."gg" alter column ts_title type tsvector using ts_title::tsvector; """
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def gg_cdc(conp_pg):
    sql="select * from etl.gg_cdc  "
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","cdc"]
    datadict={"html_key":BIGINT(),
    "price":NUMERIC(),'bd_key':BIGINT(),'fa_butime':TIMESTAMP(),'create_time':TIMESTAMP(),'ts_tile':TSVECTOR()}
    pg2pg(sql,'gg_cdc',conp_hawq,conp_pg,chunksize=10000,datadict=datadict)
    sql="""alter table "cdc"."gg_cdc" alter column ts_title type tsvector using ts_title::tsvector; """
    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""insert into public.gg 
    select * from cdc.gg_cdc"""
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def get_max_html_key(conp=None):
    if conp is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    else:conp_pg=conp
    sql="select max(html_key) from public.gg"
    df=db_query(sql,dbtype="postgresql",conp=conp_pg)
    max_html_key=df.iat[0,0]
    return max_html_key


def est(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]

    sql="select tablename from pg_tables where schemaname='public' "

    df=db_query(sql,dbtype='postgresql',conp=conp_pg)

    if 'gg' not in df['tablename']:
        print("gg表不存在，需要全量导入")
        gg_all(conp_pg)
        gg_ts(conp_pg)
        gg_pk(conp_pg)
    else:
        print("gg表已经存在，增量更新")
        max_html_key=get_max_html_key(conp_pg)
        gg.est('cdc',max_html_key)
        gg_cdc(conp_pg)


def restart(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]

    sql="drop table public.gg"

    db_command(sql,dbtype='postgresql',conp=conp_pg)

    est(conp_pg)

