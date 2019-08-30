from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlhawq.dst.page.core import add_quyu_tmp,restart_quyu_tmp
import traceback

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<阿里云<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def add_quyu_aliyun(quyu):
    conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','page']
    add_quyu_tmp(quyu,conp_hawq)

def restart_quyu_aliyun(quyu):
    conp_hawq=['gpadmin','since2015','192.168.4.179','base_db','page']
    restart_quyu_tmp(quyu,conp_hawq)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>阿里云>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def add_quyu(quyu,loc='aliyun'):
    if loc=='aliyun':
        add_quyu_aliyun(quyu)
    # elif loc=='kunming':
    #     add_quyu_kunming(quyu,tag)

def restart_quyu(quyu,loc='aliyun'):
    if loc=='aliyun':
        restart_quyu_aliyun(quyu)
    # elif loc=='kunming':
    #     add_quyu_kunming(quyu,tag)

def add_quyu_all(loc='aliyun',total=None):

    failed_quyus=[]
    cost_total=0

    df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zlsys|^zlshenpi|^jianzhu')

    select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
    ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])
    df.index=df['sheng']
    if total is None:total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zlsys|^zlshenpi|^jianzhu' """,
        dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    total_remain=total
    for sheng in  df.index:
        sheng_quyus=df.at[sheng,'sheng_quyus']
        total_sheng=len(sheng_quyus)
        total_sheng_remain=total_sheng
        print("全量同步省%s"%sheng,sheng_quyus,"合计%d个"%len(sheng_quyus))

        bg=time.time()
        for quyu in sheng_quyus:
            total_sheng_remain-=1
            total_remain-=1
            print("开始同步%s"%quyu)
            print("全局共%d个,全省共%d个,全省还剩%d个,全国还剩%d个"%(total,total_sheng,total_sheng_remain,total_remain))
            print('已经出错的',failed_quyus)
            try:
                add_quyu(quyu,loc)
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()
            if total_remain==0:break
        if total_remain==0:break


#add_quyu_all()