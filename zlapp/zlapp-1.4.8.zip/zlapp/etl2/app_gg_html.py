import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict

#gg_html 更新相对独立
def gg_html_all(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="select html_key,page,quyu from v3.t_gg   "
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    datadict={"html_key":BIGINT(),
    "page":TEXT(),'quyu':TEXT()}
    pg2pg(sql,'gg_html',conp_hawq,conp_pg,chunksize=10000,datadict=datadict)



def gg_html_pk(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="alter table public.gg_html add constraint pk_gg_html_html_key primary key(html_key) "
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def get_max_html_key(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="select max(html_key) from public.gg"
    df=db_query(sql,dbtype="postgresql",conp=conp_pg)
    max_html_key=df.iat[0,0]
    return max_html_key



def gg_html_cdc(conp_pg=None,max_html_key):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","cdc"]

    print('max_html_key',max_html_key)
    sql="select html_key,page,quyu from v3.t_gg where html_key>%d  "%max_html_key

    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
   
    datadict={"html_key":BIGINT(),
    "page":TEXT(),'quyu':TEXT()}
    pg2pg(sql,'gg_html_cdc',conp_hawq,conp_pg,chunksize=10000,datadict=datadict)

    sql="insert into public.gg_html select * from cdc.gg_html_cdc"
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def est(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]

    sql="select tablename from pg_tables where schemaname='public' "

    df=db_query(sql,dbtype='postgresql',conp=conp_pg)

    if 'gg_html' not in df['tablename']:
        print("gg_html表不存在，需要全量导入")
        gg_html_all(conp_pg)
        print("全量导入完毕，建立主键")
        gg_html_pk(conp_pg)
    else:
        print("gg表已经存在，增量更新")
        max_html_key=get_max_html_key(conp_pg)
        gg_html_cdc(conp_pg,max_html_key)