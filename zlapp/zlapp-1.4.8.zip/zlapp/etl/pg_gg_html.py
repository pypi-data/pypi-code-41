import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql="drop table if exists %s.gg_html "%schema 
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="select html_key,guid,page into %s.gg_html from cdc.t_gg_app"%(schema)
    db_command(sql,dbtype="postgresql",conp=conp)





def est2():
    sql="select html_key,page,quyu from v3.t_gg   "
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    conp_pg=["postgres","since2015","192.168.4.188","bid","public"]

    pg2pg(sql,'gg_html1',conp_hawq,conp_pg,chunksize=10000)
