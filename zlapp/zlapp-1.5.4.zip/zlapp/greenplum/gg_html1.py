import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time

def est_gg_html():
    sql="""
    CREATE TABLE if not exists "public"."gg_html" (
    "html_key" bigint NOT NULL,
    page text  
    ) distributed by(html_key)"""

    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def update_gg_html():
    bg=time.time()
    est_gg_html()
    sql="""truncate public.gg_html;"""
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])
    sql="""
    
    insert into "public".gg_html(html_key,  page) 

    select html_key,  page
     from et_gg_html
    """
    #where not exists(select 1 from gg_meta  as b where a.html_key=b.html_key ) and fabu_time>='1900-01-01' and fabu_time<'2019-12-31'
    print(sql)
    conp=['gpadmin','since2015','192.168.4.206','biaost','public']

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])

    ed=time.time()
    cost=int(ed-bg)
    print("gg_html 全表重导入耗时%s 秒"%cost)