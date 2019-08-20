from zlapp.greenplum import gg ,gg_meta,gg_zhongbiao,core_pxf ,qy_base,qy_zcry
from zlapp.greenplum import qy_zz,qy_zhongbiao,t_gg_ent_bridge,t_person
from zlapp.greenplum import app_qy_zcry,app_qy_zz,app_qy_query,app_gg_zhongbiao,gg_html 

from zlapp.greenplum import bd_dt ,t_bd_xflv

def update_gg_meta():
    core_pxf.et_gg_meta()

    gg_meta.update_gg_meta()


def update_gg():
    core_pxf.et_gg_meta()

    gg.update_gg()


def update_qy_base():
    core_pxf.et_qy_base()

    qy_base.update_qybase()

def update_qy_zcry():
    core_pxf.et_qy_zcry()
    qy_zcry.update_qy_zcry()

def update_qy_zz():
    core_pxf.et_qy_zz()
    qy_zz.update_qy_zz()

def update_t_person():
    core_pxf.et_t_person()
    t_person.update_t_person()

def update_gg_zhongbiao():
    core_pxf.et_gg_meta()
    gg_zhongbiao.update_gg_zhongbiao()


def update_qy_zhongbiao():
    qy_zhongbiao.update_qy_zhongbiao()

def update_app_gg_zhongbiao():
    app_gg_zhongbiao.update_app_gg_zhongbiao()

def update_app_qy_zz():
    app_qy_zz.update_app_qy_zz()

def update_app_qy_zcry():
    app_qy_zcry.update_app_qy_zcry()

def update_t_gg_ent_bridge():
    t_gg_ent_bridge.update_t_gg_ent_bridge()

def update_app_qy_query():

    app_qy_query.update_app_qy_query()




def update_all():
    update_gg_meta()
    update_gg()
    gg_html.update_gg_html()
    update_qy_base()
    update_qy_zcry()
    update_qy_zz()
    update_t_person()
    update_gg_zhongbiao()
    update_qy_zhongbiao()
    update_app_gg_zhongbiao()
    update_app_qy_zz()
    update_app_qy_zcry()
    update_t_gg_ent_bridge()
    update_app_qy_query()
    bd_dt.update_bd_dt()
    t_bd_xflv.update_t_bd_xflv()









