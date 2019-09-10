from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.src.core import add_quyu_tmp,restart_quyu_tmp
import traceback
#developer   zhulong!123
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<阿里云<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def get_conp_aliyun(quyu):
    conp=['postgres','since2015','192.168.4.201','postgres','public']
    sql="select usr,password,host,db,schema from cfg where quyu='%s' "%quyu
    df=db_query(sql,dbtype="postgresql",conp=conp)
    conp=df.values[0].tolist()
    return conp

def add_quyu_aliyun(quyu,tag):
    conp_pg=get_conp_aliyun(quyu)
    conp_hawq=['developer','zhulong!123','192.168.4.183:5433','base_db','public']
    add_quyu_tmp(quyu,conp_pg,conp_hawq,tag)

def restart_quyu_aliyun(quyu):
    conp_pg=get_conp_aliyun(quyu)
    conp_hawq=['developer','zhulong!123','192.168.4.183:5433','base_db','public']
    restart_quyu_tmp(quyu,conp_pg,conp_hawq)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>阿里云>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<昆明<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def get_conp_kunming(quyu):
    conp=['postgres','since2015','192.168.169.89','postgres','public']
    sql="select usr,password,host,db,schema from cfg where quyu='%s' "%quyu
    df=db_query(sql,dbtype="postgresql",conp=conp)
    conp=df.values[0].tolist()
    return conp

def add_quyu_kunming(quyu,tag):
    conp_pg=get_conp_kunming(quyu)
    conp_hawq=['developer','zhulong!123','192.168.169.91:5433','base_db','public']
    add_quyu_tmp(quyu,conp_pg,conp_hawq,tag)

def restart_quyu_kunming(quyu):
    conp_pg=get_conp_kunming(quyu)
    conp_hawq=['developer','zhulong!123','192.168.169.91:5433','base_db','public']
    restart_quyu_tmp(quyu,conp_pg,conp_hawq)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>昆明>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>





def add_quyu(quyu,tag='all',loc='aliyun'):
    print("---------------------------add--airflow(%s)-->src---------------------------------"%quyu)
    if loc=='aliyun':
        add_quyu_aliyun(quyu,tag)
    elif loc=='kunming':
        add_quyu_kunming(quyu,tag)

def restart_quyu(quyu,loc='aliyun'):
    print("---------------------------restart--airflow(%s)-->src---------------------------------"%quyu)
    if loc=='aliyun':
        restart_quyu_aliyun(quyu)
    elif loc=='kunming':
        restart_quyu_kunming(quyu)













########add_all###################

def add_quyu_all(loc='aliyun'):

    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zljianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zljianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public']).iat[0,0]
    df.index=df['sheng']

    total_remain=total
    for sheng in  df.index:
        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            #测试几个
            #if total-total_remain==5:return
            total_sheng_remain-=1
            total_remain-=1
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                add_quyu(quyu,'all',loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()





def add_quyu_all_zlsys(loc='aliyun'):

    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlsys')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlsys' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlsys')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlsys' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public']).iat[0,0]


    df.index=df['sheng']

    total_remain=total
    for sheng in  df.index:

        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            #测试几个
            #if total-total_remain==5:return
            total_sheng_remain-=1
            total_remain-=1
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                add_quyu(quyu,'all',loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()



def add_quyu_all_zlshenpi(loc='aliyun'):

    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':

        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlshenpi')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlshenpi' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:

        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu~'^zlshenpi')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu~'^zlshenpi' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public']).iat[0,0]

    df.index=df['sheng']

    total_remain=total
    for sheng in  df.index:
        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            #测试几个
            #if total-total_remain==5:return
            total_sheng_remain-=1
            total_remain-=1
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                add_quyu(quyu,'all',loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()
