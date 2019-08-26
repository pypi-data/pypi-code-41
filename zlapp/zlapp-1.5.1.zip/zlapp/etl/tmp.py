import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    tbname='t_gg_ent_bridge'
    sql="""
select * from m1.n_gg where zhongbiaoren is not null
"""
    datadict={"html_key":BIGINT(),'href':TEXT(),"ggtype":TEXT(),'quyu':TEXT(),'kzj':NUMERIC(),'zhongbiaojia':NUMERIC()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)
