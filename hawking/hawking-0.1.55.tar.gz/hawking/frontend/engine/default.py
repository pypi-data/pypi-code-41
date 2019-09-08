import logging
import logging.config
import os
import time
import grpc

from hawking_proto import hawking_pb2, hawking_pb2_grpc

# Default search engine
class HawkingSearchEngine():
    def __init__(self):
        self.namespaces = {}
        self.indexer_host = '127.0.0.1'
        self.indexer_port = 50000
        self.channel = grpc.insecure_channel('{}:{}'.format(self.indexer_host, self.indexer_port))

    # request to index single entity
    # returns: true, if new entry was added, false if existing entry was updated
    def index(self, namespace, uuid, body):
        raise ValueError("Not supported!")

    # search through entities (match query with embeddings of entity)
    # count - max number of results
    # query - search query
    #
    # returns: array of tuples (reference -> score)
    def search(self, namespace, count, query, entity_type='text'):
        results = []

        with grpc.insecure_channel('{}:{}'.format(self.indexer_host, self.indexer_port)) as channel:
            stub = hawking_pb2_grpc.SearchStub(channel)

            st = time.time()
            type = (hawking_pb2.SearchRequest.EntityType.TEXT
                    if entity_type == 'text'
                    else hawking_pb2.SearchRequest.EntityType.IMAGE)
            logging.info('Type: {}. Query: "{}"'.format(type, query))
            request = hawking_pb2.SearchRequest(max_results=count, query=query, type=type)
            response = stub.Get(request)
            logging.info('Search results:\n')
            for result in response.results:
                snippet = '%s' % (result.document.body)
                results.append((snippet, result.score))
            logging.info(results)
            et = (time.time() - st) * 1000.0
            logging.info('elapsed time: %d ms' % et)

        return results


logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logging.conf'))
logging.config.fileConfig(logging_conf_path)
engine = HawkingSearchEngine()
