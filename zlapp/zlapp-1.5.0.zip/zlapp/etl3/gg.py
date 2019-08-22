import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
from zlhawq.data import zhulong_diqu_dict ,zl_diqu_dict




######

def gg_all_prt1():

    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_prt1表")
    sql="truncate table etl.gg_all_prt1;"
    db_command(sql,dbtype="postgresql",conp=conp)

    print("gg_all_prt1 ,预计350秒")
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
     FROM v3.t_gg where quyu!~'^zlsys|^zlshenpi|^qycg'  )

    ,b as (select * from bid.t_bd_gg where quyu!~'^zlsys|^zlshenpi|^qycg' ) 

    ,c as (select * from m1.n_gg where quyu!~'^zlsys|^zlshenpi|^qycg'  )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_all_prt2():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_prt2表")
    sql="truncate table etl.gg_all_prt2;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^zlsys' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])


    print("prt2 预计10秒")
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
     FROM v3.t_gg where quyu in('zlsys_sichuan_yaanshi')  )

    ,b as (select * from bid.t_bd_gg where quyu in('zlsys_sichuan_yaanshi')  ) 

    select a.*
    ,b.bd_key
    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiao_hxr') 
    else coalesce(m1.get_js_v(info,'zbr'),m1.get_js_v(info,'zbdl') ) end  as person

    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiaojia') 
    else m1.get_js_v(info,'kzj') end  as price

     from a left join b on a.html_key=b.html_key

    """
    sql=sql.replace("""'zlsys_sichuan_yaanshi'""",txt )
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_all_prt3():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("清空etl.gg_prt3表")
    sql="truncate table etl.gg_all_prt3;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^zlshenpi' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])

    sql="""
    insert into etl.gg_all_prt3
      select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

        etl.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
                ,create_time

        from v3.t_gg where quyu in ('zlshenpi_fujiansheng') 
            """
    sql=sql.replace("""'zlshenpi_fujiansheng'""",txt)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_all_prt4():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("清空etl.gg_prt4表")
    sql="truncate table etl.gg_all_prt4;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^qycg' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])


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
     FROM v3.t_gg where quyu in('qycg_ec_chalieco_com')  )

    ,b as (select * from bid.t_bd_gg where quyu in('qycg_ec_chalieco_com') ) 

    ,c as (select * from m1.n_gg where quyu in('qycg_ec_chalieco_com') )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """

    sql=sql.replace("'qycg_ec_chalieco_com'",txt)
    print(sql)
#     db_command(sql,dbtype="postgresql",conp=conp)




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




# def gg_all_prt4():
#     conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

#     print("清空etl.gg_prt4表")
#     sql="truncate table etl.gg_all_prt4;"
#     db_command(sql,dbtype="postgresql",conp=conp)

#     sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
#     and partitionname~'^qycg' order by  partitionname 

#     """
#     df=db_query(sql,dbtype="postgresql",conp=conp)
#     quyus=list(df['partitionname'].values)
#     #arr=['qycg']
#     total=len(quyus)
#     totoal_finished=0
#     costs=0
#     bg=time.time()


#     print("qycg 部分")

#     costs=0
#     bg=time.time()

#     for quyu in quyus:
#         try:
#             print("开始注入quyu----%s"%quyu)
#             gg_all_prt4_quyu(quyu)
#         except:
#             traceback.print_exc()
#         finally:
#             total-=1
#             ed=time.time()
#             cost=int(ed-bg)
#             costs+=cost
#             print("耗时----%s秒,还剩%d个,总耗时%d秒"%(cost,total,costs))
#             bg=time.time()





####



def gg_cdc_prt1(max_html_key):

    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_cdc_prt1表")
    sql="truncate table etl.gg_cdc_prt1;"
    db_command(sql,dbtype="postgresql",conp=conp)

    print("gg_cdc_prt1 ,预计350秒")
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
     FROM v3.t_gg where quyu!~'^zlsys|^zlshenpi|^qycg' and html_key>100000000  )

    ,b as (select * from bid.t_bd_gg where quyu!~'^zlsys|^zlshenpi|^qycg' ) 

    ,c as (select * from m1.n_gg where quyu!~'^zlsys|^zlshenpi|^qycg'  )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """
    sql=sql.replace('100000000',str(max_html_key))
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_cdc_prt2(max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]

    print("清空etl.gg_cdc_prt2表")
    sql="truncate table etl.gg_cdc_prt2;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^zlsys' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])


    print("prt2 预计10秒")
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
    etl.quyu2xzqh(quyu) as xzqh
    , etl.title2ts(gg_name) as ts_title
     FROM v3.t_gg where quyu in('zlsys_sichuan_yaanshi')  and html_key>100000000  )

    ,b as (select * from bid.t_bd_gg where quyu in('zlsys_sichuan_yaanshi')  ) 

    select a.*
    ,b.bd_key
    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiao_hxr') 
    else coalesce(m1.get_js_v(info,'zbr'),m1.get_js_v(info,'zbdl') ) end  as person

    ,case when  a.ggtype~'中标|评标|结果' then  m1.get_js_v(info,'zhongbiaojia') 
    else m1.get_js_v(info,'kzj') end  as price

     from a left join b on a.html_key=b.html_key

    """
    sql=sql.replace("""'zlsys_sichuan_yaanshi'""",txt )
    sql=sql.replace('100000000',str(max_html_key))
    db_command(sql,dbtype="postgresql",conp=conp)



def gg_cdc_prt3(max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("清空etl.gg_cdc_prt3表")
    sql="truncate table etl.gg_cdc_prt3;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^zlshenpi' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])

    sql="""
    insert into etl.gg_cdc_prt3
      select html_key,    guid,   gg_name,    href,   fabu_time, '拟建项目'::text as  ggtype, '拟建项目'::text as jytype, diqu,   quyu,

        etl.zlshenpi_extpage(page,fabu_time,info,quyu) as info 
                ,create_time

        from v3.t_gg where quyu in ('zlshenpi_fujiansheng')  and html_key>100000000 
            """
    sql=sql.replace("""'zlshenpi_fujiansheng'""",txt)
    sql=sql.replace('100000000',str(max_html_key))
    db_command(sql,dbtype="postgresql",conp=conp)




def gg_cdc_prt4(max_html_key):
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("清空etl.gg_cdc_prt4表")
    sql="truncate table etl.gg_cdc_prt4;"
    db_command(sql,dbtype="postgresql",conp=conp)

    sql="""select partitionname from pg_partitions where schemaname='v3' and tablename='t_gg'
    and partitionname~'^qycg' order by  partitionname 

    """
    df=db_query(sql,dbtype="postgresql",conp=conp)

    quyus=list(df['partitionname'].values)
    print(quyus)
    txt=','.join(["'%s'"%quyu for quyu in quyus])


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
     FROM v3.t_gg where quyu in('qycg_ec_chalieco_com') and html_key>100000000   )

    ,b as (select * from bid.t_bd_gg where quyu in('qycg_ec_chalieco_com') ) 

    ,c as (select * from m1.n_gg where quyu in('qycg_ec_chalieco_com') )

    select a.*
    ,b.bd_key
    ,coalesce(c.zhongbiaoren,c.zhaobiaoren,c.zbdl) as person 
    ,coalesce(c.zhongbiaojia,c.kzj) as price

     from a left join b on a.html_key=b.html_key  left join c on c.html_key=a.html_key 

    """
    sql=sql.replace("'qycg_ec_chalieco_com'",txt)
    sql=sql.replace('100000000',str(max_html_key))
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)


def gg_all_union():
    conp=["gpadmin","since2015","192.168.4.179","base_db","public"]
    print("gg_all部分，先清空")
    sql="truncate etl.gg_all"
    db_command(sql,dbtype="postgresql",conp=conp)

    print("prt1")
    sql1="""insert into etl.gg_all 
    select 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    coalesce(etl.xzqh2diqu(xzqh),diqu) diqu,
    quyu,
    info,
    create_time,
    xzqh,
    ts_title,
    bd_key,
    person,
    price
    from etl.gg_all_prt1"""
    db_command(sql1,dbtype="postgresql",conp=conp)

    print("prt2")
    sql2="""insert into etl.gg_all 
    select 
    html_key,
    guid,
    gg_name,
    href,
    fabu_time,
    ggtype,
    jytype,
    coalesce(etl.xzqh2diqu(xzqh),diqu) diqu,
    quyu,
    info,
    create_time,
    xzqh,
    ts_title,
    bd_key,
    person,
    price
    from etl.gg_all_prt2"""
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


