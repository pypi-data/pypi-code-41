import time 
from lmf.dbv2 import db_command,db_query
import traceback
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC






def est_qy_zz():
    sql="""
    CREATE TABLE if not exists "etl"."qy_zz" (
    "href" text COLLATE "default",
    "zzbh" text COLLATE "default",
    "gsd" text COLLATE "default",
    "jglx" text COLLATE "default",
    "zzmc" text COLLATE "default",
    "bgdate" text COLLATE "default",
    "eddate" text COLLATE "default",
    "fbjg" text COLLATE "default",
    "tydm" text COLLATE "default",
    "fddbr" text COLLATE "default",
    "zzlb" text COLLATE "default",
    "entname" text COLLATE "default",
    "jgdz" text COLLATE "default",
    "qita" text COLLATE "default",
    "ent_key" int8,
    "xzqh" text COLLATE "default",
    "zzcode" text COLLATE "default",
    "alias" text COLLATE "default"
    )
    distributed by (ent_key)

    """

    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']

    db_command(sql,dbtype="postgresql",conp=conp)

def et_qy_zz():
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']
    sql="""select tablename from pg_tables where schemaname='etl' """
    df=db_query(sql,dbtype="postgresql",conp=conp)
    if 'et_qy_zz' in df['tablename'].tolist():
        print("et_qy_zz 已经存在，跳过")
        return None
    sql="""
    create  external table etl.et_qy_zz(href text    ,zzbh text ,    gsd text ,  jglx text , zzmc text , bgdate text ,   eddate text ,   fbjg text , tydm text , fddbr text ,    
    zzlb text   ,entname text , jgdz text   ,qita    text ,ent_key bigint,  xzqh text   ,zzcode text ,  alias text  )
            LOCATION ('pxf://public.qy_zz?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
            FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    db_command(sql,dbtype="postgresql",conp=conp)


def update_qy_zz():
    et_qy_zz()
    est_qy_zz()
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']
    sql="""    truncate table "etl".qy_zz;"""
    print(sql)
    db_command(sql,dbtype="postgresql",conp=conp)
    sql="""
    insert into "etl".qy_zz(href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias)
    SELECT href,    zzbh,   gsd ,jglx,  zzmc,   bgdate, eddate  ,fbjg,  tydm,   fddbr   ,zzlb,  entname,    jgdz,   qita    ,ent_key,   xzqh    ,zzcode ,alias   FROM "etl"."et_qy_zz";
        """
    print(sql)

    db_command(sql,dbtype="postgresql",conp=conp)