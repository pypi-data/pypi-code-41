import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC
import time 

def est_gg_html_quyu(quyu,conp_gp):
  
    sql="""
    CREATE TABLE if not exists etl.gg_html_%s (
    html_key bigint,
    page text
    )
    distributed by(html_key)
    """%(quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)



def get_max_html_key(quyu,conp_gp):
    #conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
    max_html_key=db_query("select max_html_key from etl.t_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp).iat[0,0]

    return max_html_key

def pre_quyu_cdc(quyu,conp_gp):
    max_html_key=get_max_html_key(quyu,conp_gp)
    print("更新前最大html_key :",max_html_key)
    est_gg_html_quyu(quyu,conp_gp)
    sql="truncate table etl.gg_html_%s;"%quyu

    sql1="insert into etl.gg_html_%s select html_key,page.tran_page(page) as page from src.t_gg where quyu='%s' and html_key>%d "%(quyu,quyu,max_html_key)

    sql=sql+sql1
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    df=db_query("select max(html_key),count(*) from etl.gg_html_%s "%quyu,dbtype="postgresql",conp=conp_gp)
    cnt=df.iat[0,1]
    print("此次更新数据 %d 条"%cnt)
    max_html_key1=df.iat[0,0]

    return max_html_key1


def et_gg_me_quyu(quyu,conp_app):

    sql="""
    drop external table if exists cdc.et_gg_meta_anhui_anqing_ggzy;
    create  external table  cdc.et_gg_meta_anhui_anqing_ggzy(html_key bigint,
    guid text,
    gg_name text,
    href text,
    fabu_time timestamp,
    ggtype text,
    jytype text,
    diqu text,
    quyu text,
    info text,
    create_time timestamp,
    xzqh text,
    ts_title text,
    bd_key bigint,
    person text,
    price text,
    zhaobiaoren text,
    zhongbiaoren text,
    zbdl text,
    zhongbiaojia float,
    kzj float8,
    xmmc text,
    xmjl text,
    xmjl_zsbh text,
    xmdz text,
    zbfs text,
    xmbh text,
    mine_info text
    )
    LOCATION ('pxf://etl.gg_meta_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=gpadmin&PASS=since2015')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app)


def insert_into(quyu,conp_app):
    et_gg_meta_quyu(quyu,conp_app)
    sql="""
    insert into "public".gg_meta(html_key,  guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   ,create_time,   xzqh,   ts_title    ,bd_key ,person ,price
    ,zhaobiaoren    ,zhongbiaoren   ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh, xmdz,   zbfs    ,xmbh,  mine_info) 

    select html_key,    guid,   gg_name,    href,   fabu_time,  ggtype, jytype, diqu    ,quyu   ,info   
    ,create_time,   xzqh,   ts_title::tsvector as ts_title  ,bd_key ,person ,price::numeric as price
    ,zhaobiaoren    ,zhongbiaoren   ,zbdl   ,zhongbiaojia   ,kzj    ,xmmc   ,xmjl   ,xmjl_zsbh, xmdz,   zbfs    ,xmbh,  mine_info
     from cdc.et_gg_meta_%s 
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app)



def update(quyu,conp_gp,conp_app):
    print("----------------------%s 开始更新--------------------------------------- "%quyu)
    max_html_key1=pre_quyu_cdc(quyu,conp_gp)



    if max_html_key1 is  None:
        print("更新后最大html_key :",max_html_key1)
        return None
    print("更新后最大html_key :",max_html_key1)
    insert_into(quyu,conp_app)

    sql="update etl.t_html_key set max_html_key=%d where quyu='%s' "%(max_html_key1,quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)

# quyu="anhui_anqing_ggzy"
# conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
# conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']

# update(quyu,conp_gp,conp_app)