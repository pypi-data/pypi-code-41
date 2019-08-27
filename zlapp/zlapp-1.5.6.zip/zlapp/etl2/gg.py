import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict




######

def gg_all_prt1_quyu(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_all_prt1
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.quyu2xzqh(quyu) as xzqh,
    etl.title2ts(gg_name) ts_title
     FROM v3.t_gg where quyu='anhui_anqing' )

    ,b as (select * from bid.t_bd_gg where quyu='anhui_anqing') 

    ,c as (select * from m1.n_gg where quyu='anhui_anqing' )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """
    sql=sql.replace('anhui_anqing',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)






def gg_all_prt1():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_prt1表")
    sql="truncate table etl.gg_all_prt1;"
    db_command(sql,dbtype="postgresql",conp=conp)

    total=sum([len(zhulong_diqu_dict[sheng]) for sheng in zhulong_diqu_dict.keys() ])
    arr=['gcjs','zfcg']
    total+=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    totoal_finished=0
    costs=0
    bg=time.time()
    shengs=zhulong_diqu_dict.keys()
    shengs=list(shengs)
    shengs.sort()
    for sheng in shengs :
        quyus=zhulong_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_all_prt1_quyu(quyu)
            except:
                traceback.print_exc()
            finally:
                total-=1
                totoal_finished+=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,完成%d个,总耗时%d秒"%(cost,total,totoal_finished,costs))
                bg=time.time()
                #if totoal_finished>3:return None

    print("gcjs  zfcg 部分")

    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_all_prt1_quyu(quyu)
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()




def gg_cdc_prt1_quyu(quyu,max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_cdc_prt1
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.quyu2xzqh(quyu) as xzqh,
    etl.title2ts(gg_name) ts_title
     FROM v3.t_gg where quyu='anhui_anqing' and html_key>%d )

    ,b as (select * from bid.t_bd_gg where quyu='anhui_anqing') 

    ,c as (select * from m1.n_gg where quyu='anhui_anqing' )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """%(max_html_key)
    sql=sql.replace('anhui_anqing',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_cdc_prt1(max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_cdc_prt1表")
    sql="truncate table etl.gg_cdc_prt1;"
    db_command(sql,dbtype="postgresql",conp=conp)

    total=sum([len(zhulong_diqu_dict[sheng]) for sheng in zhulong_diqu_dict.keys() ])
    arr=['gcjs','zfcg']
    total+=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    totoal_finished=0
    costs=0
    bg=time.time()
    shengs=zhulong_diqu_dict.keys()
    shengs=list(shengs)
    shengs.sort()
    for sheng in shengs :
        quyus=zhulong_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_cdc_prt1_quyu(quyu,max_html_key)
            except:
                traceback.print_exc()
            finally:
                total-=1
                totoal_finished+=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,完成%d个,总耗时%d秒"%(cost,total,totoal_finished,costs))
                bg=time.time()
                #if totoal_finished>10:return None

    print("gcjs  zfcg 部分")

    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_cdc_prt1_quyu(quyu,max_html_key)
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()




def gg_all_prt2_quyu(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_all_prt2
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.quyu2xzqh(quyu) as xzqh
    , etl.title2ts(gg_name) as ts_title
     FROM v3.t_gg where quyu='zlsys_yunnan_qujingshi' )

    ,b as (select * from bid.t_bd_gg where quyu='zlsys_yunnan_qujingshi') 

    select a.*
    ,b.bd_key
    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiao_hxr') 
    else coalesce(m1.get_js_v(info,'zbr'),m1.get_js_v(info,'zbdl') ) end  as person

    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiaojia') 
    else m1.get_js_v(info,'kzj') end  as price


     from a left join b on a.html_key=b.html_key 

    """
    sql=sql.replace('zlsys_yunnan_qujingshi',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_all_prt2():
    quyus=['zlsys_yunnan_qujingshi']
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_prt2部分,zlsys，先清空")
    sql="truncate etl.gg_all_prt2"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始gg_prt2部分-----zlsys")
    costs=0
    bg=time.time()
    
    total=len(quyus)
    for quyu in quyus:
        try:
            gg_all_prt2_quyu(quyu)
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()


def gg_cdc_prt2_quyu(quyu,max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_cdc_prt2
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.quyu2xzqh(quyu) as xzqh,
     etl.title2ts(gg_name)
     FROM v3.t_gg where quyu='zlsys_yunnan_qujingshi' and html_key>%d )

    ,b as (select * from bid.t_bd_gg where quyu='zlsys_yunnan_qujingshi') 

    select a.*
    ,b.bd_key
    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiao_hxr') 
    else coalesce(m1.get_js_v(info,'zbr'),m1.get_js_v(info,'zbdl') ) end  as person

    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiaojia') 
    else m1.get_js_v(info,'kzj') end  as price


     from a left join b on a.html_key=b.html_key 

    """%(max_html_key)
    sql=sql.replace('zlsys_yunnan_qujingshi',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_cdc_prt2(max_html_key):
    quyus=['zlsys_yunnan_qujingshi']
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_cdc_prt2部分,zlsys，先清空")
    sql="truncate etl.gg_cdc_prt2"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始gg_cdc_prt2部分-----zlsys")
    costs=0
    bg=time.time()
    
    total=len(quyus)
    for quyu in quyus:
        try:
            print(quyu)
            gg_cdc_prt2_quyu(quyu,max_html_key)

        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()




def gg_all_quyu_prt3(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_all_prt3
    select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

    etl.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
            ,create_time

    from v3.t_gg where quyu='%s' 
            """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp)



def gg_all_prt3():
    quyus=['zlshenpi_fujiansheng']
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_prt3部分，先清空")
    sql="truncate etl.gg_all_prt3"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始gg_prt3部分-----zlshenpi")
    costs=0
    bg=time.time()
    
    total=len(quyus)
    for quyu in quyus:
        try:
            print("开始注入quyu----%s"%quyu)

            gg_all_quyu_prt3(quyu)
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()





def gg_cdc_quyu_prt3(quyu,max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_cdc_prt3
    select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

    etl.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
            ,create_time
    from v3.t_gg where quyu='%s' and html_key>%d
            """%(quyu,max_html_key)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_cdc_prt3(max_html_key):
    quyus=['zlshenpi_fujiansheng']
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_prt3部分，先清空")
    sql="truncate etl.gg_cdc_prt3"

    db_command(sql,dbtype="postgresql",conp=conp)

    print("开始gg_cdc_prt3部分-----zlshenpi")
    costs=0
    bg=time.time()
    
    total=len(quyus)
    for quyu in quyus:
        try:
            print("开始注入quyu----%s"%quyu)

            gg_cdc_quyu_prt3(quyu,max_html_key)
        except:
            traceback.print_exc()
        finally:
            total-=1
            ed=time.time()
            cost=int(ed-bg)
            costs+=cost
            print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
            bg=time.time()



def gg_all_prt4_quyu(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_all_prt4
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.qycg_xzqh(page) as xzqh,
    etl.title2ts(gg_name) ts_title
     FROM v3.t_gg where quyu='qycg_ec_chalieco_com'  )

    ,b as (select * from bid.t_bd_gg where quyu='qycg_ec_chalieco_com') 

    ,c as (select * from m1.n_gg where quyu='qycg_ec_chalieco_com' )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """
    sql=sql.replace('qycg_ec_chalieco_com',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_all_prt4():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_prt4表")
    sql="truncate table etl.gg_all_prt4;"
    db_command(sql,dbtype="postgresql",conp=conp)

    
    arr=['qycg']
    total=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    totoal_finished=0
    costs=0
    bg=time.time()


    print("qycg 部分")

    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_all_prt4_quyu(quyu)
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()




def gg_cdc_prt4_quyu(quyu,max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    sql="""
    insert into etl.gg_cdc_prt4
    with a as (SELECT 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    diqu,
    quyu,
    info,

    create_time,
    etl.qycg_xzqh(page) as xzqh,
    etl.title2ts(gg_name) ts_title
     FROM v3.t_gg where quyu='qycg_ec_chalieco_com' and html_key=%d )

    ,b as (select * from bid.t_bd_gg where quyu='qycg_ec_chalieco_com') 

    ,c as (select * from m1.n_gg where quyu='qycg_ec_chalieco_com' )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """%(max_html_key)
    sql=sql.replace('qycg_ec_chalieco_com',quyu)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_cdc_prt4(max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_prt4表")
    sql="truncate table etl.gg_cdc_prt4;"
    db_command(sql,dbtype="postgresql",conp=conp)

    
    arr=['qycg']
    total=sum([len(zl_diqu_dict[sheng]) for sheng in  arr ])
    totoal_finished=0
    costs=0
    bg=time.time()


    print("gcjs  zfcg 部分")

    costs=0
    bg=time.time()
    for sheng in arr:
        quyus=zl_diqu_dict[sheng]
        quyus.sort()
        for quyu in quyus:
            try:
                print("开始注入quyu----%s"%quyu)
                gg_cdc_prt4_quyu(quyu,max_html_key)
            except:
                traceback.print_exc()
            finally:
                total-=1
                ed=time.time()
                cost=int(ed-bg)
                costs+=cost
                print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
                bg=time.time()




def gg_all_union():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_all部分，先清空")
    sql="truncate etl.gg_all"
    db_command(sql,dbtype="postgresql",conp=conp)

    print("prt1")
    sql1="insert into etl.gg_all select * from etl.gg_all_prt1"
    db_command(sql1,dbtype="postgresql",conp=conp)

    print("prt2")
    sql2="insert into etl.gg_all select * from etl.gg_all_prt2"
    db_command(sql2,dbtype="postgresql",conp=conp)

    print("prt3")
    sql3="""

    insert into etl.gg_all(html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,    bd_key, xzqh,ts_title,   person, price)     
    select html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,NULL::bigint as bd_key
    
     ,etl.quyu2xzqh(quyu) as xzqh
        , etl.title2ts(gg_name) as ts_title
        ,m1.get_js_v(info,'xmdw') person 
        ,m1.extprice(m1.get_js_v(info,'xmtz')) price
        from etl.gg_all_prt3 
      """
    db_command(sql3,dbtype="postgresql",conp=conp)

    print("prt4")
    sql4="""

    insert into etl.gg_all(html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,    bd_key, xzqh,ts_title,   person, price)     
    select html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,etl.xzqh2diqu(xzqh) diqu,  quyu,   info,   create_time,bd_key, xzqh,ts_title,   person, price
    from etl.gg_all_prt4

      """
    db_command(sql4,dbtype="postgresql",conp=conp)


def gg_cdc_union():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_cdc部分，先清空")
    sql="truncate etl.gg_cdc"
    db_command(sql,dbtype="postgresql",conp=conp)

    print("prt1")
    sql1="insert into etl.gg_cdc select * from etl.gg_cdc_prt1"
    db_command(sql1,dbtype="postgresql",conp=conp)

    print("prt2")
    sql2="insert into etl.gg_cdc select * from etl.gg_cdc_prt2"
    db_command(sql2,dbtype="postgresql",conp=conp)

    print("prt3")
    sql3="""

    insert into etl.gg_cdc(html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,    bd_key, xzqh,ts_title,   person, price)     
    select html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,NULL::bigint as bd_key 
    
    ,etl.quyu2xzqh(quyu) as xzqh
        , etl.title2ts(gg_name) as ts_title
        ,m1.get_js_v(info,'xmdw') person 
        ,m1.extprice(m1.get_js_v(info,'xmtz')) price
        from etl.gg_cdc_prt3 
      """
    db_command(sql3,dbtype="postgresql",conp=conp)

    print("prt4")
    sql4="""

    insert into etl.gg_cdc(html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,diqu,  quyu,   info,   create_time,    bd_key, xzqh,ts_title,   person, price)     
    select html_key,    guid    ,gg_name,   href    ,fabu_time, ggtype, jytype  ,etl.xzqh2diqu(xzqh)  as diqu,  quyu,   info,   create_time,bd_key, xzqh,ts_title,   person, price
    from etl.gg_cdc_prt4

      """
    db_command(sql4,dbtype="postgresql",conp=conp)



def gg_all_parts():
    gg_all_prt1()
    gg_all_prt2()
    gg_all_prt3()
    gg_all_prt4()

def gg_cdc_parts(max_html_key):
    gg_cdc_prt1(max_html_key)
    gg_cdc_prt2(max_html_key)
    gg_cdc_prt3(max_html_key)
    gg_cdc_prt4(max_html_key)


def gg_all():

    gg_all_parts()
    gg_all_union()

def gg_cdc(max_html_key):

    gg_cdc_parts(max_html_key)
    gg_cdc_union()





def est(tag='cdc',max_html_key=None):
    if tag=='cdc':
        if max_html_key is None:
            print("请添加参数max_html_key")
            return False 
        gg_cdc(max_html_key)
    else:
        gg_all()







