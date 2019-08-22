import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est():

    sql="select * from etl.gg_zhongbiao "
    tbname="gg_zhongbiao"
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    bg=time.time()
    datadict={"html_key":BIGINT(),"gg_name":TEXT(),"href":TEXT(),"fabu_time":TIMESTAMP(),"ggtype":TEXT(),"zhongbiaojia":NUMERIC(),"kzj":NUMERIC(),"xzqh":TEXT()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=10000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)
