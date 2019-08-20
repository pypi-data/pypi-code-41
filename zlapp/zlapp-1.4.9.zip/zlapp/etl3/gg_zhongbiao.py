import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta



def est1():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_zhongbiao部分，先清空")
    sql="truncate etl.gg_zhongbiao"
    db_command(sql,dbtype="postgresql",conp=conp)
    bg=time.time()
    sql="""
    insert into etl.gg_zhongbiao
    with a as (select * from m1.n_gg  where  zhongbiaoren!='公司' and zhongbiaoren is not null  )
    select a.*,b.gg_name,b.fabu_time, b.xzqh 
    , ts_title
      from a ,etl.gg_all b where a.html_key=b.html_key
    """
    db_command(sql,dbtype="postgresql",conp=conp)

    ed=time.time()

    cost=int(ed-bg)
    print("耗时------%d秒"%cost)


def est2():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^zlsys' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])

    sql="""
    insert into etl.gg_zhongbiao
    SELECT html_key,href,
        ggtype, quyu,   
    m1.get_js_v(info,'zhongbiao_hxr') as zhongbiaoren,

    m1.get_js_v(info,'zbr') as zhaobiaoren,
    m1.get_js_v(info,'zbdl') as zbdl,   
    m1.get_js_v(info,'zhongbiaojia') as zhongbiaojia,   
    m1.get_js_v(info,'kzj') as kzj,
    m1.get_js_v(info,'xm_name') as xmmc,
    m1.get_js_v(info,'xmjl') as xmjl,
    m1.get_js_v(info,'bd_dz') as xmdz,
    Null::text as zbfs,
    m1.get_js_v(info,'bd_bh') as xmbh,
    gg_name,
    fabu_time,
    etl.quyu2xzqh(quyu) as xzqh ,   
    etl.title2ts(gg_name) as ts_title 

     FROM "v3"."t_gg" where quyu in ('zlsys_yunnan_qujingshi') and ggtype~'中标|评标|结果';
    """
    sql=sql.replace("'zlsys_yunnan_qujingshi'",txt)
    db_command(sql,dbtype="postgresql",conp=conp)



def est():
    est1()
    est2()