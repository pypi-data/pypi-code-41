from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst import algo,bid,bid_bridge 
import traceback
from zlgp.dst import api
def add_quyu_kunming(quyu,tag='all'):
    if quyu.startswith('zlsys'):
        bid.api.add_quyu(quyu,tag,loc='kunming')

        bid_bridge.add_quyu(quyu,loc='kunming')

        api.add_quyu(quyu,loc='kunming')

    elif quyu.startswith('zlshenpi'):


        api.add_quyu(quyu,loc='kunming')

    else:

        bid.api.add_quyu(quyu,tag,loc='kunming')

        bid_bridge.add_quyu(quyu,loc='kunming')

        algo.api.add_quyu(quyu,loc='kunming')

        api.add_quyu(quyu,loc='kunming')



def restart_quyu_kunming(quyu):
    if quyu.startswith('zlsys'):
        bid.api.restart_quyu(quyu,loc='kunming')

        bid_bridge.restart_quyu(quyu,loc='kunming')

        api.restart_quyu(quyu,loc='kunming')

    elif quyu.startswith('zlshenpi'):


        api.restart_quyu(quyu,loc='kunming')
    else:

        bid.api.restart_quyu(quyu,loc='kunming')

        id_bridge.restart_quyu(quyu,loc='kunming')

        algo.api.restart_quyu(quyu,loc='kunming')

        api.restart_quyu(quyu,loc='kunming')




def add_quyu(quyu,tag='all',loc='aliyun'):
    if loc=='kunming':
        add_quyu_kunming(quyu,tag)

def restart_quyu(quyu,loc='aliyun'):
    if loc=='kunming':
        restart_quyu_kunming(quyu)



def add_quyu_all(loc='aliyun'):

    failed_quyus=[]
    cost_total=0
    if loc=='aliyun':
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zlsys|^jianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public']).iat[0,0]
    else:
        df=db_query("""with a as (SELECT quyu,split_part(quyu,'_',1) as sheng  FROM "public"."cfg" where quyu!~'^zljianzhu')

        select sheng,array_agg(quyu order by quyu asc) as sheng_quyus from a group by sheng  order by sheng
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])

        total=db_query("""select count(*) total   FROM "public"."cfg" where quyu!~'^zlsys|^jianzhu' """,
            dbtype="postgresql",conp=['postgres','since2015','192.168.189.89','postgres','public']).iat[0,0]

    df.index=df['sheng']

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
                add_quyu(quyu,'all')
                ed=time.time()
                cost=int(ed-bg)
                cost_total+=cost
                print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
            except:
                traceback.print_exc()
                failed_quyus.append(quyu)
            finally:
                bg=time.time()


def restart_quyu_all_zlshenpi(loc='aliyun'):
    if loc=='aliyun'
        df=db_query("""SELECT quyu  FROM "public"."cfg" where quyu~'^zlshenpi' order by quyu

      
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.4.201','postgres','public'])
    else:
        df=db_query("""SELECT quyu  FROM "public"."cfg" where quyu~'^zlshenpi' order by quyu

      
        ;""",dbtype="postgresql",conp=['postgres','since2015','192.168.169.89','postgres','public'])
    failed_quyus=[]
    cost_total=0
    quyus=df['quyu'].tolist()
    print(quyus)
    total=len(quyus)
    total_remain=len(quyus)
    bg=time.time()
    for quyu in quyus:
        
        total_remain-=1
        print("开始同步%s"%quyu)
        print("全局共%d个,还剩%d个"%(total,total_remain))
        print('已经出错的',failed_quyus)
        try:
            restart_quyu(quyu)
            ed=time.time()
            cost=int(ed-bg)
            cost_total+=cost
            print("耗时%d 秒,累计耗时%d 秒"%(cost,cost_total))
        except:
            traceback.print_exc()
            failed_quyus.append(quyu)
        finally:
            bg=time.time()
