#coding: utf8
from __future__ import absolute_import
from xserver.client.utils.fab import run

# project related

def install_xserver():
    run('pip install pycrypto==2.6.1')
    run('pip install fabric==1.10.1')
    run('pip install xserver')
    run('xserver install_start')
    run('xserver install_live')