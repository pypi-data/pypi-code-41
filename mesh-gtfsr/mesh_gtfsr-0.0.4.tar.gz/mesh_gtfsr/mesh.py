from .lib.rpc_pb2 import PeerTopicInfo
from .defaults import Default

class MeshGTFSR:
    def __init__(self):
        pass

    def subscribe(self):
        m = PeerTopicInfo()
        m.topic = Default.topic
        
        print(m)

    def publish(self):
        pass
    
