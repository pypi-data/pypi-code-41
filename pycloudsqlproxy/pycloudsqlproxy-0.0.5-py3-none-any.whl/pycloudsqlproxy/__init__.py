import logging
import os
import subprocess
import sys

def connect():
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.info('> Starting cloud_sql_proxy')

    netstat = subprocess.Popen(['netstat', '-peanut'], stdout=subprocess.PIPE)
    grep = subprocess.Popen(['grep', '3306'], stdin=netstat.stdout, stdout=subprocess.PIPE)
    netstat.stdout.close()
    out, err = grep.communicate()
    out = out.decode('utf-8')

    if err is not None:
        sys.exit(err)
    if out == '':
        log.info('>> cloud_sql_proxy starting')
        subprocess.Popen(['{}/cloud_sql_proxy'.format(os.path.dirname(__file__)), '-instances=icentris-ml:us-west1:ml-monat-dev=tcp:3306'])
    else:
        log.info('>> cloud_sql_proxy already open')
