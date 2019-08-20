import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC


#gg_html 更新相对独立
def gg_html_all(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="select html_key,page from src.t_gg   "
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","src"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    datadict={"html_key":BIGINT(),
    "page":TEXT()}
    pg2pg(sql,'gg_html',conp_hawq,conp_pg,chunksize=10000,datadict=datadict)



def gg_html_pk(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    #conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="alter table public.gg_html add constraint pk_gg_html_html_key primary key(html_key) "
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def get_max_html_key(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]
    sql="select max(html_key) from public.gg_html"
    df=db_query(sql,dbtype="postgresql",conp=conp_pg)
    max_html_key=df.iat[0,0]
    return max_html_key



def gg_html_cdc(max_html_key,conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","cdc"]
    conp_pg[4]='cdc'

    print('max_html_key',max_html_key)
    sql="select html_key,page from src.t_gg where html_key>%d  "%max_html_key

    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","src"]
   
    datadict={"html_key":BIGINT(),
    "page":TEXT()}
    pg2pg(sql,'gg_html_cdc',conp_hawq,conp_pg,chunksize=10000,datadict=datadict)


    sql="insert into public.gg_html select * from cdc.gg_html_cdc"
    db_command(sql,dbtype="postgresql",conp=conp_pg)


def est(conp_pg=None):
    if conp_pg is None:conp_pg=["postgres","since2015","192.168.4.188","bid","public"]

    sql="select tablename from pg_tables where schemaname='public' "

    df=db_query(sql,dbtype='postgresql',conp=conp_pg)

    if 'gg_html' not in df['tablename'].values:
        print("gg_html表不存在，需要全量导入")
        gg_html_all(conp_pg)
        print("全量导入完毕，建立主键")
        gg_html_pk(conp_pg)
    else:
        print("gg_html表已经存在，增量更新")
        max_html_key=get_max_html_key(conp_pg)
        gg_html_cdc(max_html_key,conp_pg)

def update_gg_html():
    conp_pg=['postgres','since2015','192.168.4.207','biaost','public']
    est(conp_pg)