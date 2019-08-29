# -*- coding: utf-8 -*-
from univider.indexer import Indexer

indexer = Indexer()

# indexer.save('aaaaa2fe-8d4a-4f23-bb66-ec2b5b8174f56','http://www.baidu.com','事实','陶阳每天半夜研究黑客技术')

result =  indexer.read('淘宝')
print result
