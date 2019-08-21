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

recipient = '491717626871'

now = datetime.now().strftime('%H:%M:%S')

text     = now + ': das Ã¤Ã¤h Ã¶Ã¶Ã¶ "ist" *ein* test \xF0\x9F\x98\x9C'.decode('utf8')
# text = 'ööö \U0001f604'

if __name__ == "__main__":
   print(text)
   simple_send(wa_srv,port,recipient,text)