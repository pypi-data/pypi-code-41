import logging
import time
import grpc

from hawking_proto import hawking_pb2, hawking_pb2_grpc

# Default dummy store
class DummyStore():
    def __init__(self):
        self.namespaces = {}
        self.store_host = '127.0.0.1'
        self.store_port = 42000
        self.channel = grpc.insecure_channel('{}:{}'.format(self.store_host, self.store_port))

    # store object (content_type, blob) under namespace/uuid
    # returns: uuid
    def put(self, namespace, uuid, content):
        with grpc.insecure_channel('{}:{}'.format(self.store_host, self.store_port)) as channel:
            stub = hawking_pb2_grpc.StoreStub(channel)
            logging.info('Put: "{}/{}"'.format(namespace, uuid))
            request = hawking_pb2.StorePutRequest(namespace = namespace, document=hawking_pb2.Document(uuid = uuid, body=content))
            
            return stub.Put(request).uuid

    # retrieve object (content_type, blob) by namespace/uuid
    #
    # returns: {content_type, blob}
    def get(self, namespace, uuid):
        with grpc.insecure_channel('{}:{}'.format(self.store_host, self.store_port)) as channel:
            stub = hawking_pb2_grpc.StoreStub(channel)
            logging.info('Get: "{}/{}"'.format(namespace, uuid))
            request = hawking_pb2.StoreGetRequest(namespace = namespace, uuid = uuid)
            return stub.Get(request).document.body

store = DummyStore()
