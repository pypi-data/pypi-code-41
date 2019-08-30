import grpc

from .lib.rpc_pb2 import PeerTopicInfo, PublishData, Data
from .lib.rpc_pb2_grpc import MeshStub
from .exp import MeshRPCException

class MeshRPC:
    def __init__(self, endpoint):
        c = grpc.insecure_channel(endpoint)
        self.stub = MeshStub(c)

    def subscribe(self, topic):
        m = PeerTopicInfo()
        m.topic = topic
        
        s = self.stub.Subscribe(m)

        return s

    def registerToPublish(self, topic):
        m = PeerTopicInfo()
        m.topic = topic

        try:
            p = self.stub.RegisterToPublish(m)
            return p
        except grpc.RpcError as e:
            raise MeshRPCException(e.details())

    def publish(self, topic, raw):
        pd = PublishData()
        
        pd.info.topic = topic
        pd.data.raw = raw

        try:
            res = self.stub.Publish(pd)
            return res
        except grpc.RpcError as e:
            raise MeshRPCException(e.details())
