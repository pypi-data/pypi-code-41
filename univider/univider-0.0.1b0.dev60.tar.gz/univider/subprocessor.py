# -*- coding: utf-8 -*-
import threading

from univider.logger import Logger


class Subprocessor():

    logger = Logger(__name__).getlogger()

    def __init__(self,landing,params,result):
        self.landing = landing
        self.key = params['uuid']
        self.url = params['url']
        if(result.has_key('title')):
            self.title = result['title']
        else:
            self.title = None
        if(result.has_key('html')):
            self.content = result['html']
        else:
            self.content = None

    def store_to_hbase(self):
        from univider.storager import Storager
        storager = Storager()
        storager.save_to_hbase(self.key,self.url,self.title,self.content)
        self.logger.info("stored to hbase : " + self.url)

    def store_to_hdfs(self):
        from univider.storager import Storager
        storager = Storager()
        storager.save_to_hdfs(self.key,self.url,self.title,self.content)
        self.logger.info("stored to hdfs : " + self.url)

    def index_to_es(self):
        from univider.indexer import Indexer
        indexer = Indexer()
        indexer.save(self.key,self.url,self.title,self.content)
        self.logger.info("indexed " + self.url)

    def persist(self):
        threads = []
        if("es" in self.landing):
            t1 = threading.Thread(target=self.index_to_es)
            threads.append(t1)
        if("hbase" in self.landing):
            t2 = threading.Thread(target=self.store_to_hbase)
            threads.append(t2)
        if("hdfs" in self.landing):
            t3 = threading.Thread(target=self.store_to_hdfs)
            threads.append(t3)

        for t in threads:
            t.setDaemon(True)
            t.start()
        # t.join()



