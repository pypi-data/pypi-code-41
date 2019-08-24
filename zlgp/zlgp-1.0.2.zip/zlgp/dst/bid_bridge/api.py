from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 

from zlhawq.dst.bid_bridge.core import add_quyu_tmp,restart_quyu_tmp
import traceback

#昆明云
def add_quyu_kunming(quyu,tag='all',loc='aliyun'):
    conp_hawq=['gpadmin','since2015','192.168.169.90:5433','base_db','bid']
    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        add_quyu_tmp(quyu,conp_hawq)
    elif quyu.startswith('zlsys'):
        add_quyu_tmp(quyu,conp_hawq)
    else:
        print("暂不支持 区域%s"%quyu)


def restart_quyu_kunming(quyu,tag='all',loc='aliyun'):
    conp_hawq=['gpadmin','since2015','192.168.169.90:5433','base_db','bid']
    if quyu in ['anhui_anqing_ggzy','anhui_chaohu_ggzy']:
        restart_quyu_tmp(quyu,conp_hawq)
    elif quyu.startswith('zlsys'):
        restart_quyu_tmp(quyu,conp_hawq)
    else:
        print("暂不支持 区域%s"%quyu)



def add_quyu(quyu,tag='all',loc='aliyun'):
    if loc=='kunming':
        add_quyu_kunming(quyu,tag)

def restart_quyu(quyu,tag='all',loc='aliyun'):
    if loc=='kunming':
        restart_quyu_kunming(quyu,tag)
