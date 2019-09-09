from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
import time 
from zlgp.dst.algo.core import add_quyu_tmp,restart_quyu_tmp #zlgp.dst.algo.
import traceback

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<阿里云<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def add_quyu_aliyun(quyu):
    conp_hawq=['developer','zhulong!123','192.168.4.183:5433','base_db','public']
    add_quyu_tmp(quyu,conp_hawq)

def restart_quyu_aliyun(quyu):
    conp_hawq=['developer','zhulong!123','192.168.4.183:5433','base_db','public']
    restart_quyu_tmp(quyu,conp_hawq)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>阿里云>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>




#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<昆明云<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def add_quyu_kunming(quyu):
    conp_hawq=['developer','zhulong!123','192.168.169.91:5433','base_db','algo']
    add_quyu_tmp(quyu,conp_hawq)

def restart_quyu_kunming(quyu):
    conp_hawq=['developer','zhulong!123','192.168.169.91:5433','base_db','algo']
    restart_quyu_tmp(quyu,conp_hawq)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>昆明云>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>



def add_quyu(quyu,tag='all',loc='aliyun'):
    if loc=='aliyun':
        add_quyu_aliyun(quyu)
    elif loc=='kunming':
        add_quyu_kunming(quyu)

def restart_quyu(quyu,loc='aliyun'):
    if loc=='aliyun':
        restart_quyu_aliyun(quyu)
    elif loc=='kunming':
        restart_quyu_kunming(quyu)

