import logging
import time
import grpc
import threading
import json
import numpy
import sys

from hawking_proto import hawking_pb2, hawking_pb2_grpc
from hawking.encoder.universal.encoder import UniversalTextEncoder

def _cos_similarity(f1, f2):
    n1 = numpy.linalg.norm(f1)
    n2 = numpy.linalg.norm(f2)

    return numpy.dot(f1, f2) / (n1 * n2)

class OnlineIndex():
    def __init__(self):
        self.encoder = UniversalTextEncoder()
        self.namespaces = {}
        self.checkpoint = None
        self.lock = threading.Lock()

        # TODO: move this to queue client
        self.queue_host = '127.0.0.1'
        self.queue_port = 45000
        self.retry_delay_sec = 30
        self.channel = grpc.insecure_channel('{}:{}'.format(self.queue_host, self.queue_port))
        logging.info("Start new OnlineSearchEngine")
        threading.Thread(daemon=True, name="poll-thread", target=self._poll).start()

    def _poll(self):
        stub = hawking_pb2_grpc.QueueStub(self.channel)
        while True:
            try:
                request = hawking_pb2.PollRequest(checkpoint = self.checkpoint)
                for index in stub.Poll(request):
                    logging.info('Checkpoint {} "{}/{}/{}" to index'.format(index.checkpoint, index.namespace, index.document.uuid, index.document.body))
                    features = self.encoder.encode(index.document.body)
                    self.checkpoint = index.checkpoint

                    with self.lock:
                        if index.namespace not in self.namespaces:
                            self.namespaces[index.namespace] = {}
                        self.namespaces[index.namespace][index.document.uuid] = features
            except grpc.RpcError as ex:
                logging.error(str(ex))
                logging.warn("Wait for {} seconds, before retry".format(self.retry_delay_sec))
                time.sleep(self.retry_delay_sec)
 
    def search(self, namespace, count, query):
        results = []

        features = self.encoder.encode(query)

        with self.lock:
            if namespace not in self.namespaces:
                logging.info('Namespace "{}" not indexed'.format(namespace))
                return results

            # Match query terms with embedings 
            for k,v in self.namespaces[namespace].items():
                # score is distance between 
                score = _cos_similarity(v, features)
                results.append((k, score))

        logging.info('{} results found'.format(len(results)))

        # sort results, in asc of score
        results.sort(key=lambda result: result[1], reverse=True)

        # return top #count# results
        return results[:count]

index = OnlineIndex()


# Default search engine
class OnlineSearchEngine():
    # request to index single entity
    # reference - unique way to refer
    # documents - all embeddings of entity
    #
    # returns: true, if new entry was added, false if existing entry was updated
    def index(self, namespace, uuid, body):

        # TODO: move this to queue client
        self.queue_host = '127.0.0.1'
        self.queue_port = 45000

        # TODO: move this to queue client
        with grpc.insecure_channel('{}:{}'.format(self.queue_host, self.queue_port)) as channel:
            stub = hawking_pb2_grpc.IndexStub(channel)
            logging.info('Add "{}/{}/{}"'.format(namespace, uuid, body))

            document = hawking_pb2.Document(uuid=uuid, body=body)
            request = hawking_pb2.IndexRequest(namespace=namespace, documents=[document])
            response = stub.Post(request)
            return response.inserted
            

    # search through entities (match query with embeddings of entity)
    # count - max number of results
    # query - search query
    #
    # returns: array of tuples (reference -> score)
    def search(self, namespace, count, query):
        return index.search(namespace, count, query)
        

engine = OnlineSearchEngine()