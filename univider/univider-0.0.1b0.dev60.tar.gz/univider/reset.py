# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch

from univider.settings import es_host

def reset():
    resetIndex()

def resetIndex():

    index = "cplatform"
    type = "website"

    es = Elasticsearch(es_host,
                       sniff_on_start=True,
                       sniff_on_connection_fail=True,
                       sniffer_timeout=60)

    try:
        es.indices.delete(index)
    except:
        pass

    mapping = {
        'properties':{
                'title': {
                    'analyzer': 'ik',
                    'type': 'string'
                },
                'content': {
                    'analyzer': 'ik',
                    'type': 'string'
                }
        }
    }

    es.indices.create(index)

    es.indices.put_mapping(type, mapping, index)

reset()
