import os 
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict
import time 
from lmf.dbv2 import db_command
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from  datetime  import datetime,timedelta
#先在hawq etl 的schema里生成近一个月的数据 目前的更新机制是半天一更新
#早上6点，下午三点

def t_gg_app_prt1():
    bgdate=datetime.strftime(datetime.now()-timedelta(days=30),'%Y-%m-%d')
    eddate=datetime.strftime(datetime.now()+timedelta(days=1),'%Y-%m-%d')
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_app_prt1部分，先清空")
    sql="truncate etl.t_gg_app_prt1"
    db_command(sql,dbtype="postgresql",conp=conp)
    total=sum([len(zhulong_diqu_dict[sheng]) for sheng in zhulong_diqu_dict.keys() ])
    costs=0
    bg=time.time()
    for sheng in zhulong_diqu_dict.keys():
        quyus=zhulong_diqu_dict[sheng]
        
        
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                sql="""
                insert into etl.t_gg_app_prt1
                select *   from v3.t_gg where quyu='%s'

                and fabu_time>='%s' and fabu_time<'%s'

                """%(quyu,bgdate,eddate)
                db_command(sql,dbtype="postgresql",conp=conp)

                
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()

    print("gcjs  zfcg 部分")
    arr=['gcjs','zfcg']
    total=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        
        
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                sql="""
                insert into etl.t_gg_app_prt1
                select *   from v3.t_gg where quyu='%s'

                and fabu_time>='%s' and fabu_time<'%s'

                """%(quyu,bgdate,eddate)
                db_command(sql,dbtype="postgresql",conp=conp)

                
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()


def t_gg_app_prt2():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_app_prt2部分，先清空")
    sql="truncate etl.t_gg_app_prt2"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始t_gg_app_prt2部分-----zlsys")
    costs=0
    bg=time.time()
    quyus=['zlsys_yunnan_qujingshi']
    total=len(quyus)
    for quyu in quyus:
        try:
            print("开始注入quyu----%s"%quyu)
            sql="""
            insert into etl.t_gg_app_prt2
            select *   from v3.t_gg where quyu='%s'
            """%(quyu)
            db_command(sql,dbtype="postgresql",conp=conp)

            
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()


def t_gg_app_prt3():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_app_prt3部分，先清空")
    sql="truncate etl.t_gg_app_prt3"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始t_gg_app_prt3部分-----zlshenpi")
    costs=0
    bg=time.time()
    quyus=['zlshenpi_fujiansheng']
    total=len(quyus)
    for quyu in quyus:
        try:
            print("开始注入quyu----%s"%quyu)
            sql="""
insert into etl.t_gg_app_prt3
select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

etl.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
    ,   page    ,create_time

from v3.t_gg where quyu='%s' 
            """%(quyu)
            db_command(sql,dbtype="postgresql",conp=conp)

            
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()




def t_gg_app():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("t_gg_app部分，先清空")
    sql="truncate etl.t_gg_app"
    db_command(sql,dbtype="postgresql",conp=conp)
    quyus=['t_gg_app_prt1','t_gg_app_prt2','t_gg_app_prt3']
    for quyu in quyus:

            print("开始注入----%s"%quyu)
            sql="""
            insert into etl.t_gg_app
            select *   from  etl.%s

            """%(quyu)
            db_command(sql,dbtype="postgresql",conp=conp)



##############################to_pg

def t_gg_app_pg():

    sql="select * from etl.t_gg_app "
    tbname="t_gg_app"
    conp_hawq=["gpadmin","since2015",'192.168.4.179','base_db',"etl"]
    conp_pg=["postgres","since2015",'192.168.4.188','bid',"cdc"]
    bg=time.time()
    datadict={"html_key":BIGINT(),'guid':TEXT(),"gg_name":TEXT(),"href":TEXT(),"fabu_time":TIMESTAMP(),"ggtype":TEXT(),
    "jytype":TEXT(),"diqu":TEXT(),"quyu":TEXT(),"info":TEXT(),"page":TEXT(),"create_time":TIMESTAMP(),"bd_key":BIGINT(),"xzqh":TEXT(),"person":TEXT(),"price":NUMERIC()}
    pg2pg(sql,tbname,conp_hawq,conp_pg,chunksize=5000,datadict=datadict)
    ed=time.time()
    cost=int(ed-bg)
    print("耗时%s秒"%cost)



def est():
    t_gg_app_prt1()

    t_gg_app_prt2()

    t_gg_app_prt3()
    t_gg_app()
    
    t_gg_app_pg()

