import time 
from lmf.dbv2 import db_command,db_query,db_write
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

import time 

def est_gg_zhongbiao_quyu(quyu,conp_gp):
    sql="""
    CREATE TABLE if not exists "etl"."gg_zhongbiao_%s" (
    "html_key" int8,
    "href" text COLLATE "default",
    "ggtype" text COLLATE "default",
    "quyu" text COLLATE "default",
    "zhongbiaoren" text COLLATE "default",
    "zhaobiaoren" text COLLATE "default",
    "zbdl" text COLLATE "default",
    "zhongbiaojia" numeric,
    "kzj" numeric,
    "xmmc" text COLLATE "default",
    "xmjl" text COLLATE "default",
    "xmdz" text COLLATE "default",
    "zbfs" text COLLATE "default",
    "xmbh" text COLLATE "default",
    "gg_name" text COLLATE "default",
    "fabu_time" timestamp(6),
    "xzqh" text COLLATE "default",
    "ts_title" text,
    "ent_key" int8
    )
    distributed by (html_key)"""%quyu
    db_command(sql,dbtype="postgresql",conp=conp_gp)


def write_meta(conp_app,conp_gp):
    #,conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    #conp_gp['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
    sql="""SELECT quyu,max(html_key) as max_html_key FROM "public"."gg_zhongbiao" 
    group by quyu
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_app)

    db_write(df,'gg_zhongbiao_html_key',dbtype="postgresql",conp=conp_gp)



# def write_qy_zhongbiao(conp_gp)



def get_max_html_key(quyu,conp_gp):
    #conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
    
    df=db_query("select max_html_key from etl.gg_zhongbiao_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp)
    if df.empty:return None
    max_html_key=df.iat[0,0]
    return max_html_key

def pre_quyu_cdc(quyu,conp_gp):
    max_html_key=get_max_html_key(quyu,conp_gp)
    if max_html_key is None:
        print("该区域不存在")
        return 
    print("更新前最大html_key :",max_html_key)
    est_gg_zhongbiao_quyu(quyu,conp_gp)
    sql="truncate table etl.gg_zhongbiao_%s;"%quyu

    sql1="""
    insert into etl.gg_zhongbiao_%s( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,   xmdz ,
           zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key)

     with a as ( 
    select html_key,  href ,   ggtype ,quyu ,   zhongbiaoren, zhaobiaoren ,zbdl  ,zhongbiaojia::numeric zhongbiaojia  
    ,  kzj, xmmc,  xmjl ,   xmdz ,zbfs  ,  xmbh , gg_name,fabu_time ,  xzqh , ts_title 
        from dst.gg_meta  as  t1 
    where   zhongbiaoren is not null and html_key>%d and zhongbiaoren is not null and quyu='%s' )


    select a.*,b.ent_key from a left join "etl".qy_base as b  on a.zhongbiaoren=b.jgmc  
    """%(quyu,max_html_key,quyu)

    sql=sql+sql1
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp_gp)
    df=db_query("select max(html_key),count(*) from etl.gg_zhongbiao_%s "%quyu,dbtype="postgresql",conp=conp_gp)
    cnt=df.iat[0,1]
    print("此次更新数据 %d 条"%cnt)
    max_html_key1=df.iat[0,0]

    return max_html_key1



def et_gg_zhongbiao_quyu(quyu,conp_app):

    sql="""
    drop external table if exists cdc.et_gg_zhongbiao_anhui_anqing_ggzy;
    create  external table  cdc.et_gg_zhongbiao_anhui_anqing_ggzy(
    "html_key" int8,
    "href" text ,
    "ggtype" text ,
    "quyu" text ,
    "zhongbiaoren" text ,
    "zhaobiaoren" text ,
    "zbdl" text ,
    "zhongbiaojia" numeric,
    "kzj" numeric,
    "xmmc" text ,
    "xmjl" text ,
    "xmdz" text ,
    "zbfs" text ,
    "xmbh" text ,
    "gg_name" text ,
    "fabu_time" timestamp(6),
    "xzqh" text ,
    "ts_title" text,
    "ent_key" int8
    )
    LOCATION ('pxf://etl.gg_zhongbiao_anhui_anqing_ggzy?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.183:5433/base_db&USER=gpadmin&PASS=since2015')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    sql=sql.replace("anhui_anqing_ggzy",quyu)

    db_command(sql,dbtype="postgresql",conp=conp_app)


def insert_into(quyu,conp_app):
    et_gg_zhongbiao_quyu(quyu,conp_app)
    sql="""
    insert into "public".gg_zhongbiao( html_key,  href ,   ggtype , quyu ,   zhongbiaoren,    zhaobiaoren ,zbdl  ,  zhongbiaojia  ,  kzj, xmmc,    xmjl ,   xmdz ,
           zbfs  ,  xmbh ,   gg_name, fabu_time ,  xzqh ,   ts_title,ent_key)

    select html_key,  href ,   ggtype ,quyu ,   zhongbiaoren, zhaobiaoren ,zbdl  ,zhongbiaojia::numeric zhongbiaojia  
    ,  kzj, xmmc,  xmjl ,   xmdz ,zbfs  ,  xmbh , gg_name,fabu_time ,  xzqh , ts_title::tsvector as ts_tile,ent_key
     from cdc.et_gg_zhongbiao_%s 
    """%(quyu)
    db_command(sql,dbtype="postgresql",conp=conp_app)


#def qy_zhongbiao_cdc()


def update(quyu,conp_gp,conp_app):
    print("----------------------%s 开始更新--------------------------------------- "%quyu)
    max_html_key1=pre_quyu_cdc(quyu,conp_gp)



    if max_html_key1 is  None:
        print("更新后最大html_key :",max_html_key1)
        return None
    print("更新后最大html_key :",max_html_key1)
    insert_into(quyu,conp_app)

    sql="update etl.gg_zhongbiao_html_key set max_html_key=%d where quyu='%s' "%(max_html_key1,quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)


quyu="anhui_anqing_ggzy"
conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
pre_quyu_cdc(quyu,conp_gp)
#update(quyu,conp_gp,conp_app)