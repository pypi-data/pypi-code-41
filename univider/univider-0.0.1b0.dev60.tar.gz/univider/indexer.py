# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch, SerializationError

from univider.settings import es_host

class Indexer:

    # create_namespace 'spider'
    # create 'spider:cplatform', {NAME => 'w', VERSIONS => 1, TTL => 2592000, BLOCKCACHE => true}

    host = es_host

    index = "cplatform"
    type = "website"

    es = Elasticsearch(host,
                   sniff_on_start=True,
                   sniff_on_connection_fail=True,
                   sniffer_timeout=60)

    def save(self,key,url,title,content):

        if(title != None and title != '' and content != None and content != '' ):
            body = {
                'url':url,
                'title':title,
                'content':content
            }
            self.es.index(self.index, self.type, body, key)
        elif(title != None and title != ''  ):
            body = {
                'url':url,
                'title':title
            }
            self.es.index(self.index, self.type, body, key)
        elif(content != None and content != ''  ):
            try:
                body = {
                    'url':url,
                    'content':content
                }
                self.es.index(self.index, self.type, body, key)
            except SerializationError,e:
                body = {
                    'url':url,
                    'content':content.decode('utf8')
                }
                self.es.index(self.index, self.type, body, key)
        else:
            body = {
                'url':url,
            }
            self.es.index(self.index, self.type, body, key)



    def read(self,keyword):

        body = {
            "query":{
                "bool":{
                    "should":[
                        {"match":{"url":keyword}},
                        {"match":{"title":keyword}},
                        {"match":{"content":keyword}},
                    ]
                }
            }
        }

        result = self.es.search(self.index, self.type, body)

        count = result["hits"]["total"]

        print "keyword:" + keyword
        print "count:" + str(count)

        for row in result["hits"]["hits"]:
            print row
            # score = row["_score"]
            # id = row["_id"]
            # title = row["_source"]["title"]
            # content = row["_source"]["content"]
            # print " score:" + str(score) + " id:" + id + " title:" + title + " content:" + content

        # print result["hits"]["hits"][0]["_source"]["news_content"]