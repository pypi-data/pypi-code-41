
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from zlhawq.data import zlsys_diqu_dict 
def bd_quyu(quyu):
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]


    sql="""
    insert into etl.bd 
    with a as (select 
    distinct on(bd_guid)
    m1.get_js_v(info,'bd_guid') as bd_guid
    ,m1.get_js_v(info,'bd_name') as bd_name 
    ,m1.get_js_v(info,'bd_bh') as bd_bh
    ,m1.get_js_v(info,'zbr') as zhaobiaoren  

    ,m1.get_js_v(info,'zbdl') as zbdl  
    ,m1.get_js_v(info,'kzj') as kzj  
    ,m1.get_js_v(info,'xm_name') as xm_name  
    ,fabu_time,quyu ,etl.quyu2xzqh(quyu) as xzqh


     from v3.t_gg where quyu='zlsys_yunnan_qujingshi' order by bd_guid,fabu_time asc )


    select b.bd_key,a.* from a left join bid.t_bd_1_prt_zlsys_yunnan_qujingshi as b on a.bd_guid=b.bd_guid
    """
    sql=sql.replace('zlsys_yunnan_qujingshi',quyu)
    db_command(sql,dbtype="postgresql",conp=conp_hawq)


def bd():
    quyus=zlsys_diqu_dict['zlsys']
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("bd部分,zlsys，先清空")
    sql="truncate etl.bd"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始bd部分-----zlsys")
    costs=0
    bg=time.time()
    quyus.sort()
    total=len(quyus)
    for quyu in quyus:
        print(quyu)
        try:
            bd_quyu(quyu)
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()


def est():
    bd()
    
    # datadict={"bd_key":BIGINT(),'bd_guid':TEXT(),"bd_name":TEXT(),"bd_bh":TEXT(),"zhaobiaoren":TEXT(),
    # "zbdl":TEXT(),"kzj":NUMERIC(),'xm_name':TEXT(),"fabu_time":TIMESTAMP(),'quyu':TEXT()}
    # pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)