# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from snakeskin.protos.common import common_pb2 as snakeskin_dot_protos_dot_common_dot_common__pb2
from snakeskin.protos.peer import events_pb2 as snakeskin_dot_protos_dot_peer_dot_events__pb2


class DeliverStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.Deliver = channel.stream_stream(
        '/protos.Deliver/Deliver',
        request_serializer=snakeskin_dot_protos_dot_common_dot_common__pb2.Envelope.SerializeToString,
        response_deserializer=snakeskin_dot_protos_dot_peer_dot_events__pb2.DeliverResponse.FromString,
        )
    self.DeliverFiltered = channel.stream_stream(
        '/protos.Deliver/DeliverFiltered',
        request_serializer=snakeskin_dot_protos_dot_common_dot_common__pb2.Envelope.SerializeToString,
        response_deserializer=snakeskin_dot_protos_dot_peer_dot_events__pb2.DeliverResponse.FromString,
        )


class DeliverServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def Deliver(self, request_iterator, context):
    """deliver first requires an Envelope of type ab.DELIVER_SEEK_INFO with
    Payload data as a marshaled orderer.SeekInfo message,
    then a stream of block replies is received
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeliverFiltered(self, request_iterator, context):
    """deliver first requires an Envelope of type ab.DELIVER_SEEK_INFO with
    Payload data as a marshaled orderer.SeekInfo message,
    then a stream of **filtered** block replies is received
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DeliverServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'Deliver': grpc.stream_stream_rpc_method_handler(
          servicer.Deliver,
          request_deserializer=snakeskin_dot_protos_dot_common_dot_common__pb2.Envelope.FromString,
          response_serializer=snakeskin_dot_protos_dot_peer_dot_events__pb2.DeliverResponse.SerializeToString,
      ),
      'DeliverFiltered': grpc.stream_stream_rpc_method_handler(
          servicer.DeliverFiltered,
          request_deserializer=snakeskin_dot_protos_dot_common_dot_common__pb2.Envelope.FromString,
          response_serializer=snakeskin_dot_protos_dot_peer_dot_events__pb2.DeliverResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'protos.Deliver', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
