# -*- coding: utf-8 -*-
from univider.storager import Storager

storager = Storager()

storager.save_to_hbase('aaaaa2fe-8d4a-4f23-bb66-ec2b5b8174f56','http://www.baidu.com','百度','啦啦啦啦啦啦这是内容')

result =  storager.read_from_hbase('aaaaa2fe-8d4a-4f23-bb66-ec2b5b8174f56')
print result


