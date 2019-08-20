
from lmf.dbv2 import db_query ,db_command


def et_gg_meta():
    conp=["postgres","since2015","192.168.4.201","postgres","public"]

    quyus=db_query("select quyu from cfg",dbtype="postgresql",conp=conp)['quyu'].tolist()

    txt=':'.join(quyus)

    sql="""
    drop external table if exists public.et_gg_meta;
    create  external table public.et_gg_meta(html_key bigint,
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
    LOCATION ('pxf://dst.gg_meta?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.179:5432/base_db&USER=gpadmin&PASS=since2015&PARTITION_BY=quyu:enum&RANGE=anhui_anqing_ggzy:anhui_chaohu_ggzy')
    FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    sql=sql.replace("anhui_anqing_ggzy:anhui_chaohu_ggzy",txt)

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def et_qy_base():
    sql="""
    drop external table if exists public.et_qy_base;
    create  external table public.et_qy_base(ent_key bigint,    jgmc text,  tydm text,  zch text,   jgdm text,  entid text, clrq  timestamp(6),
        jgdz text,  fddbr text ,    jyfw text   ,jjhy    text, jglx text,   zczj    text,
    zczj_bz text,   zczj_sj text,   zczj_sj_bz text,    taxdm    text, fromtime timestamp(6),    totime  timestamp(6) , djbumen text, jyzt   text,
    engname text,bondnum text,  zggm text,  email    text, phone text,  website  text,staff_info    text,
    alias text, diaoxiaodate text,  diaoxiaoreason   text,zhuxiaodate text, zhuxiaoreason text, logo text,  sh_info text,   xzqh  text  )
        LOCATION ('pxf://public.qy_base?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])




def et_qy_zcry():
    sql="""
        drop external table if exists public.et_qy_zcry;
    create  external table public.et_qy_zcry(ent_key bigint,    tydm text,  xzqh text,  ryzz_code text,
    href text,  name    text ,gender text,  zjhm text,  zj_type text,   zclb text,  zhuanye  text, zsbh text,   yzh  text ,youxiao_date text,   entname text, person_key bigint  )
        LOCATION ('pxf://public.qy_zcry?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015&PARTITION_BY=person_key:int&RANGE=1:5000000&INTERVAL=10000')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])


def et_qy_zz():
    sql="""
    drop external table if exists public.et_qy_zz;
    create  external table public.et_qy_zz(href text    ,zzbh text ,    gsd text ,  jglx text , zzmc text , bgdate text ,   eddate text ,   fbjg text , tydm text , fddbr text ,    
    zzlb text   ,entname text , jgdz text   ,qita    text ,ent_key bigint,  xzqh text   ,zzcode text ,  alias text  )
            LOCATION ('pxf://public.qy_zz?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
            FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])



def et_t_person():
    sql="""
        drop external table if exists public.et_t_person;
    create  external table public.et_t_person(person_key bigint,    name text,  zj_type text,   zjhm  text )
        LOCATION ('pxf://public.t_person?PROFILE=JDBC&JDBC_DRIVER=org.postgresql.Driver&DB_URL=jdbc:postgresql://192.168.4.188:5432/bid&USER=postgres&PASS=since2015')
        FORMAT 'CUSTOM' (FORMATTER='pxfwritable_import');
    """
    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])




