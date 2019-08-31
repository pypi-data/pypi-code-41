import logging
import os
import subprocess
import sys

def connect():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.info('> Starting cloud_sql_proxy')

    def check_running():
        log.info('>> cloud_sql_proxy - check_running called')
        netstat = subprocess.Popen(['netstat', '-peanut'], stdout=subprocess.PIPE)
        for line in netstat.stdout:
            txt = line.decode('utf-8')

            if '3306' in txt:
                els = txt.split()
                log.info('>> cloud_sql_proxy listening on {}'.format(els[3]))
                return True
        return False

    if check_running() == False:
        log.info('>> cloud_sql_proxy starting')
        subprocess.Popen(['{}/cloud_sql_proxy'.format(os.path.dirname(__file__)), '-instances=icentris-ml:us-west1:ml-monat-dev=tcp:3306'])
    else:
        log.info('>> cloud_sql_proxy already open')
