
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"public"]
    tbname='bd'
    user,passwd,host,db,schema=conp_pg
    sql="drop table if exists %s.bd "%schema 
    db_command(sql,dbtype="postgresql",conp=conp_pg)

    sql="""

    with a as (select 
    distinct on(bd_guid)
    m1.get_js_v(info,'bd_guid') as bd_guid
    ,m1.get_js_v(info,'bd_name') as bd_name 
    ,m1.get_js_v(info,'bd_bh') as bd_bh
    ,m1.get_js_v(info,'zbr') as zhaobiaoren  

    ,m1.get_js_v(info,'zbdl') as zbdl  
    ,m1.get_js_v(info,'kzj') as kzj  
    ,m1.get_js_v(info,'xm_name') as xm_name  
    ,fabu_time,quyu 


     from v3.t_gg where quyu='zlsys_yunnan_qujingshi' order by bd_guid,fabu_time asc )


    select b.bd_key,a.* from a left join bid.t_bd_1_prt_zlsys_yunnan_qujingshi as b on a.bd_guid=b.bd_guid
    """
    datadict={"bd_key":BIGINT(),'bd_guid':TEXT(),"bd_name":TEXT(),"bd_bh":TEXT(),"zhaobiaoren":TEXT(),
    "zbdl":TEXT(),"kzj":NUMERIC(),'xm_name':TEXT(),"fabu_time":TIMESTAMP(),'quyu':TEXT()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)