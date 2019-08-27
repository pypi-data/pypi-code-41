from zlapp.cdc import gg_meta,t_gg_ent_bridge
from zlapp.cdc import gg ,gg_zhongbiao,qy_zhongbiao,app_qy_zz,app_qy_zcry,app_qy_query

def pre():

    conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
    gg_meta.write_meta(conp_app,conp_gp)
    gg.write_meta(conp_app,conp_gp)
    gg_zhongbiao.write_meta(conp_app,conp_gp)

#quyu="anhui_chizhou_ggzy"
def add_quyu_app(quyu):
    conp_app=['gpadmin','since2015','192.168.4.206','biaost','public']
    conp_gp=['gpadmin','since2015','192.168.4.183:5433','base_db','etl']
    pre_quyu_data(quyu,conp_gp)
    insert_into(quyu,conp_app)


def pre_quyu_data(quyu,conp_gp):
    gg_meta.pre_quyu_cdc(quyu,conp_gp)

    gg.pre_quyu_cdc(quyu,conp_gp)

    gg_zhongbiao.pre_quyu_cdc(quyu,conp_gp)

    qy_zhongbiao.pre_qy_zhongbiao(quyu,conp_gp)

    t_gg_ent_bridge.pre_t_gg_ent_bridge(quyu,conp_gp)

    app_qy_zz.pre_app_qy_zz(quyu,conp_gp)
    app_qy_zcry.pre_app_qy_zcry(quyu,conp_gp)
    app_qy_query.pre_app_qy_query(quyu,conp_gp)


def insert_into(quyu,conp_app):
    gg_meta.insert_into(quyu,conp_app)

    gg.insert_into(quyu,conp_app)

    gg_zhongbiao.insert_into(quyu,conp_app)

    qy_zhongbiao.insert_into(quyu,conp_app)

    app_qy_zz.insert_into(quyu,conp_app)

    app_qy_zcry.insert_into(quyu,conp_app)

    t_gg_ent_bridge.insert_into(quyu,conp_app)

    app_qy_query.insert_into(quyu,conp_app)