import grpc
import dict_to_protobuf
from mesh_rpc.mesh import MeshRPC
from mesh_rpc.exp import MeshRPCException

from .lib.rpc_pb2 import PeerTopicInfo
from .lib.rpc_pb2_grpc import MeshStub
from .lib.gtfs_realtime_pb2 import FeedMessage
from .defaults import Default

class MeshGTFSR(MeshRPC):
    def __init__(self, endpoint='127.0.0.1:5555'):
        super().__init__(endpoint)

    def subscribe(self):

        s = super().subscribe(Default.topic)

        feed = FeedMessage()

        try:
            for msg in s:
                feed.ParseFromString(msg.raw)
                yield feed
        except grpc.RpcError as e:
            raise MeshRPCException(e.details())
        
    def registerToPublish(self):
        try:
            super().registerToPublish(Default.topic)
        except MeshRPCException as e:
            raise 

    def publish(self, d):

        if isinstance(d, dict):
            d["header"]["gtfs_realtime_version"] = "2.0"
            feed = FeedMessage()
            dict_to_protobuf.dict_to_protobuf(d, feed)
            raw = feed.SerializeToString()
        else:
            raw = d

        try:
            res = super().publish(Default.topic, raw)
        except MeshRPCException as e:
            raise 
    
