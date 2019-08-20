import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def est():
    conp=["postgres","since2015",'192.168.4.188','bid',"public"]
    user,passwd,host,db,schema=conp
    sql1="""
    create or replace function public.quyu2ts(quyu text) returns text 
    as 
    $$

    txt=quyu.split('_')

    txt=' '.join(txt)
    return txt 


    $$ language plpython3u; 

    create or replace function public.title2ts(name text) returns text 
    as 
    $$
    import jieba 

    arr=filter(lambda x:len(x)>1, jieba.lcut(name))

    result=' '.join(arr)

    return result 

    $$ language plpython3u; 


    """

    db_command(sql1,dbtype="postgresql",conp=conp)

    print('更新gg')
    print("先truncate gg表 再插入")
    bg=time.time()
    sql_tmp="""    truncate table %s.gg;"""%(schema)
    db_command(sql_tmp,dbtype="postgresql",conp=conp)
    sql2="""

    insert into %s.gg(
    html_key,guid, gg_name,   href,   fabu_time,   ggtype, jytype, diqu,   quyu    ,  create_time ,info
    ,xzqh,bd_key,person,price   
    ,ts_title,ts_quyu
    )

    select  distinct on(guid)
    html_key,guid, gg_name,   href,   fabu_time,   ggtype, jytype, diqu,   quyu    ,  create_time,info,
    xzqh,bd_key,person,price ,
    title2ts(gg_name)::tsvector as ts_title,quyu2ts(quyu)::tsvector as ts_quyu

    from cdc.t_gg_app 
    """%(schema)
    db_command(sql2,dbtype="postgresql",conp=conp)

    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)



