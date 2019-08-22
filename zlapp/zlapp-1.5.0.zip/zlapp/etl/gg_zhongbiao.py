import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta



def est():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_zhongbiao部分，先清空")
    sql="truncate etl.gg_zhongbiao"
    db_command(sql,dbtype="postgresql",conp=conp)
    bg=time.time()
    sql="""
    insert into etl.gg_zhongbiao
    with a as (select * from m1.n_gg  where  zhongbiaoren!='公司' and zhongbiaoren is not null  )
    select a.*,b.gg_name,b.fabu_time,etl.quyu2xzqh(quyu) as xzqh 
      from a ,m1.n_gg_time b where a.html_key=b.html_key
    """
    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()

    cost=int(ed-bg)
    print("耗时------%d秒"%cost)



