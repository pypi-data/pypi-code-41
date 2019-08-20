import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta

def est():

    sql="select * from etl.bd"
    tbname="bd"
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"public"]
    bg=time.time()
    datadict={"bd_key":BIGINT(),'bd_guid':TEXT(),"bd_name":TEXT(),"bd_bh":TEXT(),"zhaobiaoren":TEXT(),
    "zbdl":TEXT(),"kzj":NUMERIC(),'xm_name':TEXT(),"fabu_time":TIMESTAMP(),'quyu':TEXT()}

    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=10000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)