from zlapp.cdc import gg_meta,t_gg_ent_bridge
from zlapp.cdc import gg ,gg_zhongbiao,qy_zhongbiao,app_qy_zz,app_qy_zcry,app_qy_query
from lmf.dbv2 import db_query,db_command ,db_write
from zlapp.greenplum import gg_html 
from lmf.bigdata import pg2pg 
from sqlalchemy.dialects.postgresql import  TEXT,BIGINT,TIMESTAMP,NUMERIC

def pre_meta():
    conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    conp_gp=['developer','zhulong!123','192.168.4.183:5433','base_db','etlmeta']
    sql="""
    with a as (select  
    quyu,max(html_key) as max_gg_meta
    from "public".gg_meta group by quyu )

    ,b as (
    select  
    quyu,max(html_key) as max_gg
    from "public".gg group by quyu

    )
    ,c as (
    select  
    quyu,max(html_key) as max_gg_zhongbiao
    from "public".gg_zhongbiao group by quyu
    )
    select a.*, coalesce(max_gg,0) max_gg, coalesce(max_gg_zhongbiao,0)  max_gg_zhongbiao from a left join b on a.quyu=b.quyu left join c on a.quyu=c.quyu 
    """
    df=db_query(sql,dbtype="postgresql",conp=conp_app)

    db_write(df,'t_html_key',dbtype="postgresql",conp=conp_gp)

def quyu_not_exists(quyu,conp_gp):
    df=db_query("select quyu from etlmeta.t_html_key ",dbtype="postgresql",conp=conp_gp)
    if quyu not in df['quyu'].tolist():
        db_command("insert into etlmeta.t_html_key(quyu, max_gg_meta,max_gg  ,max_gg_zhongbiao) values('%s',0,0,0)"%quyu,dbtype="postgresql",conp=conp_gp)

#quyu="anhui_chizhou_ggzy"
def add_quyu_app(quyu,loc="aliyun"):

    conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    conp_gp=['developer','zhulong!123','192.168.4.183:5433','base_db','etl']
    conp_pg=["postgres",'since2015','192.168.4.207','biaost','cdc']
    quyu_not_exists(quyu,conp_gp)
    print("---------------------------add--dst(%s)-->app---------------------------------"%quyu)


    max_html_key1=gg_meta.pre_quyu_cdc(quyu,conp_gp)

    max_html_key2=gg.pre_quyu_cdc(quyu,conp_gp)

    max_html_key3=gg_zhongbiao.pre_quyu_cdc(quyu,conp_gp)

    qy_zhongbiao.pre_qy_zhongbiao(quyu,conp_gp)

    t_gg_ent_bridge.pre_t_gg_ent_bridge(quyu,conp_gp)

    app_qy_zz.pre_app_qy_zz(quyu,conp_gp)
    app_qy_zcry.pre_app_qy_zcry(quyu,conp_gp)
    app_qy_query.pre_app_qy_query(quyu,conp_gp)
    print("gg_html----------------------------")
    max_html_key=gg_meta.get_max_html_key(quyu,conp_gp)
    sql="select html_key,page from src.t_gg where html_key>%d and quyu='%s' "%(max_html_key,quyu)


   
    datadict={"html_key":BIGINT(),
    "page":TEXT()}

    sql1="truncate table cdc.gg_html_cdc;"
    db_command(sql1,dbtype="postgresql",conp=conp_pg)
    pg2pg(sql,'gg_html_cdc',conp_gp,conp_pg,chunksize=10000,datadict=datadict,if_exists='replace')
    print("gg_html_cdc写入完毕")

    sql="insert into public.gg_html select * from cdc.gg_html_cdc as b  where not exists(select html_key from  gg_html as a where a.html_key=b.html_key)"
    db_command(sql,dbtype="postgresql",conp=conp_pg)

    #gg_html.update_gg_html()


    #m1,m2,m3=db_query("select max_gg_meta,max_gg,max_gg_zhongbiao from etlmeta.t_html_key where quyu='%s'"%quyu,dbtype="postgresql",conp=conp_gp).loc[0,:].tolist()
    if max_html_key1 is None:
        print("更新后最大html_key :",max_html_key1)
        return None
    print("待插入数据准备完成,即将往app里insert ")

    gg_meta.insert_into(quyu,conp_app)
    sql="update etlmeta.t_html_key set max_gg_meta=%d where quyu='%s' "%(max_html_key1,quyu)
    db_command(sql,dbtype='postgresql',conp=conp_gp)
    print("更新后最大html_key :",max_html_key1)

    if max_html_key2 is None:
        print("更新后最大html_key :",max_html_key1)
    else:
        gg.insert_into(quyu,conp_app)
        sql="update etlmeta.t_html_key set max_gg=%d where quyu='%s' "%(max_html_key2,quyu)
        db_command(sql,dbtype='postgresql',conp=conp_gp)
        print("更新后最大html_key :",max_html_key2)

    if max_html_key3 is None:
        print("更新后最大html_key :",max_html_key3)
    else:
        gg_zhongbiao.insert_into(quyu,conp_app)
        sql="update etlmeta.t_html_key set max_gg_zhongbiao=%d where quyu='%s' "%(max_html_key3,quyu)
        db_command(sql,dbtype='postgresql',conp=conp_gp)
        print("更新后最大html_key :",max_html_key3)


    qy_zhongbiao.insert_into(quyu,conp_app)

    app_qy_zz.insert_into(quyu,conp_app)

    app_qy_zcry.insert_into(quyu,conp_app)

    t_gg_ent_bridge.insert_into(quyu,conp_app)

    app_qy_query.insert_into(quyu,conp_app)