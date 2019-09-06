from lmf.dbv2 import db_query ,db_command

def et_gg_meta_quyu():

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

    db_command(sql,dbtype="postgresql",conp=['gpadmin','since2015','192.168.4.206','biaost','public'])
