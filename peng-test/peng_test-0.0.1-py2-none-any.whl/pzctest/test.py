# -*- coding=utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def run():
	res = requests.get('https://www.baidu.com/')
	soup = BeautifulSoup(res.text,'lxml')
	print res.text.decode('utf-8').encode('gbk','ignore')
	
if __name__ == "__main__":
	run()