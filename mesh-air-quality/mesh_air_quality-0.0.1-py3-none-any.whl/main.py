import grpc

from mesh_rpc.mesh import MeshRPC
from .lib.air_quality_pb2 import FeedMessage, DataPoint
from .defaults import Default

import dict_to_protobuf

class MeshAirQuality(MeshRPC):
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
            print('Err: ' + e.details())
    
    def registerToPublish(self):
        super().registerToPublish(Default.topic)

    def publish(self, d):
        d["header"]["air_quality_version"] = "0.0.1"
        
        feed = FeedMessage()

        dict_to_protobuf.dict_to_protobuf(d, feed)

        raw = feed.SerializeToString()

        res = super().publish(Default.topic, raw)
        print(res)
    
