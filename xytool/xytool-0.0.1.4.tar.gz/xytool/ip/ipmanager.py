#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from requests import *
from xytool.db.dbmanager import get_all_ip
from xytool.db.database_block import func_database

class IpManager:
    def check_all_ips(self):
        '''
        按周期轮询
        '''
        pass
        # 
        # 检查已经存在ip地址，可以使用等级+1，不能使用删除（轮询）
        # 当数量不足时，重新爬取，去重后存入数据库
    def get_allips_in_db(self):
        print(get_all_ip())

    def update_ips_level(self):
        pass
    
    def get_ips_from_freewebsite(self):
        pass

def IPList_61():
      for q in [1,2]:
        url = 'http://www.66ip.cn/'+str(q)+'.html'
        html = Requestdef.get_page(url)
        if html != None:
            #print(html)
            iplist = BeautifulSoup(html,'lxml')
            iplist = iplist.find_all('tr')
            i=2
            for ip in iplist:
                if i<=0:
                    loader=''
                    #print(ip)
                    j=0
                    for ipport in ip.find_all('td',limit=2):
                        if j==0:
                            loader+=ipport.text.strip()+':'
                        else:
                            loader+=ipport.text.strip()
                        j=j+1
                    Requestdef.inspect_ip(loader)
                i = i - 1
        time.sleep(1)


def main():
    IpManager().get_allips_in_db()

if __name__ == '__main__':
    main()

    # 检查已经存在ip地址，可以使用等级+1，不能使用删除（轮询）

    # 爬取已知ip地址提供商网址
    # IP地址、端口、代理、地理位置信息获取count(数量), types(模式),protocol(协议),country(国家),area(地区),(types类型(0高匿名，1透明)，protocol(0 http,1 https http),country(国家),area(省市))
    # 测试地址是否可用
    # 根据具体业务使用代理（检测ip是否可用需要开放方法）


    