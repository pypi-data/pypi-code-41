from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst.core import add_quyu_tmp,restart_quyu_tmp
import traceback


def add_quyu_kunming(quyu):
    conp=['gpadmin','since2015','192.168.169.90:5433','base_db','public']

    add_quyu_tmp(quyu,conp)



def restart_quyu_kunming(quyu):
    conp=['gpadmin','since2015','192.168.169.90:5433','base_db','public']

    restart_quyu_tmp(quyu,conp)



def add_quyu_aliyun(quyu):
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']

    add_quyu_tmp(quyu,conp)



def restart_quyu_aliyun(quyu):
    conp=['gpadmin','since2015','192.168.4.183:5433','base_db','public']

    restart_quyu_tmp(quyu,conp)


def add_quyu(quyu,loc='aliyun'):
    if loc=='kunming':
        add_quyu_kunming(quyu)
    else:
        add_quyu_aliyun(quyu)



def restart_quyu(quyu,loc='aliyun'):
    if loc=='kunming':
        restart_quyu_kunming(quyu)
    else:
        restart_quyu_aliyun(quyu)