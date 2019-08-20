import cat_helper
import time
import cat
from cat_helper import *


#@cat_helper.cat_wrapper('kd-test', 'hxa', 'wrapper2')
#def fun():
#    print '---------start------------'
#    time.sleep(3)
#    print '----------end-------------'
#    raise ValueError

#fun()

init('kd-test')
stage_begin('lh', 'test6')
#cat.Transaction('test1', 'test')
#cat.log_event('test', 'test1', '0')
time.sleep(2)
stage_begin('lh', 'test6')
time.sleep(2)
stage_end('lh', 'test6')
#stage_end('lh', 'test6', False)


