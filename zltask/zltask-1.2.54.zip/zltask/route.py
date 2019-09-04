import json
import re

from lmf.dbv2 import db_query


def get_settings(quyu,loc=None):

    if loc == "aliyun" or loc is None:
        conp = ['postgres', 'since2015', '192.168.4.201', 'postgres', 'public']
    elif loc == "kunming":
        conp = ['postgres', 'since2015', '192.168.169.89', 'postgres', 'public']
    else:
        conp = loc

    sql="select * from public.cfg where quyu='%s' "%(quyu)
    df=db_query(sql,dbtype="postgresql",conp=conp)

    conp1=[df.at[0,'usr'],df.at[0,'password'],df.at[0,'host'],df.at[0,'db'],df.at[0,'schema']]
    settings={}
    col=[ 'total', 'num', 'cdc_total', 'html_total','headless', 'pageloadstrategy', 'pageloadtimeout', 'ipNum', 'thread_retry', 'retry', 'add_ip_flag', 'page_retry',
     'image_show_gg', 'image_show_html', 'get_ip_url', "long_ip_url", "long_ip_num", "long_ip",'info']

    for w in col:

        if df.at[0,w] is not None or w == 'info':settings[w]=df.at[0,w]

    return conp1,settings





def task_quyu(quyu,loc=None,**krg):
    """
    from zlsrc.anhui import anhui_anqing_ggzy ;anhui_anqing_ggzy.work(conp1,**settings)

    :param quyu: 将要运行的quyu
    :param loc: 连接cfg表连接代号  参数值为 'aliyun' , 'kunming' , '标准conp格式(list格式) eg:['username', 'passwd', 'host', 'db', 'schema']'
    :return:
    """

    conp1,settings=get_settings(quyu,loc)

    sheng=quyu.split('_')[0]

    settings.update(**krg)
    settings.update({"loc":loc})

    print(quyu, settings)

    if sheng in ['qg','qycg','daili']:
        sheng='zlcommon'

    if sheng == 'zljianzhu':
        quyu=re.split('_\d',quyu)[0]

    exec("from zlsrc.{sheng} import {quyu};{quyu}.work({conp1},**{settings})"
        .format(sheng=sheng, quyu=quyu, conp1=conp1, settings=settings))


# task_quyu('anhui_anqing_ggzy',conp='kunming')


# sheng="zljianzhu"
# quyu="zljianzhu_qiyexx_0"
#
# if sheng == 'zljianzhu':
#     quyu = re.split('_\d', quyu)[0]
#
# conp1=conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"]
#
# settings={"total":2,"headless":True,"add_ip_flag":True,"num":1,"flag":0}
#
# exec("from zlsrc.{sheng} import {quyu};{quyu}.work({conp1},**{settings})"
#      .format(sheng=sheng,quyu=quyu,conp1=conp1,settings=settings))

# from zlsrc.anhui import anhui_anqing_ggzy ;anhui_anqing_ggzy.work(conp1,**settings)