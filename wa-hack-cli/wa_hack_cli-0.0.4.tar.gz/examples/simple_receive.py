#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
from wa_hack_cli import *

# define variables
wa_srv   = '192.168.123.38'
port     = 9009
routes = '491717626871,491797994359, 491717626871-1441519872'

now = datetime.now().strftime('%H:%M:%S')


if __name__ == "__main__":
   # print(text)
   simple_receive(wa_srv,port,routes)