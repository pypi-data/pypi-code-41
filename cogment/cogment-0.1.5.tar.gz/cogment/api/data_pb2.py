# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cogment/api/data.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cogment.api import common_pb2 as cogment_dot_api_dot_common__pb2
from cogment.api import agent_pb2 as cogment_dot_api_dot_agent__pb2
from cogment.api import environment_pb2 as cogment_dot_api_dot_environment__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='cogment/api/data.proto',
  package='cogment',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x16\x63ogment/api/data.proto\x12\x07\x63ogment\x1a\x18\x63ogment/api/common.proto\x1a\x17\x63ogment/api/agent.proto\x1a\x1d\x63ogment/api/environment.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x94\x01\n\rDatalogSample\x12\x10\n\x08trial_id\x18\x01 \x01(\t\x12-\n\x0cobservations\x18\x02 \x01(\x0b\x32\x17.cogment.ObservationSet\x12 \n\x07\x61\x63tions\x18\x03 \x03(\x0b\x32\x0f.cogment.Action\x12 \n\x07rewards\x18\x04 \x03(\x0b\x32\x0f.cogment.Rewardb\x06proto3')
  ,
  dependencies=[cogment_dot_api_dot_common__pb2.DESCRIPTOR,cogment_dot_api_dot_agent__pb2.DESCRIPTOR,cogment_dot_api_dot_environment__pb2.DESCRIPTOR,google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])




_DATALOGSAMPLE = _descriptor.Descriptor(
  name='DatalogSample',
  full_name='cogment.DatalogSample',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='trial_id', full_name='cogment.DatalogSample.trial_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='observations', full_name='cogment.DatalogSample.observations', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='actions', full_name='cogment.DatalogSample.actions', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='rewards', full_name='cogment.DatalogSample.rewards', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=151,
  serialized_end=299,
)

_DATALOGSAMPLE.fields_by_name['observations'].message_type = cogment_dot_api_dot_environment__pb2._OBSERVATIONSET
_DATALOGSAMPLE.fields_by_name['actions'].message_type = cogment_dot_api_dot_common__pb2._ACTION
_DATALOGSAMPLE.fields_by_name['rewards'].message_type = cogment_dot_api_dot_agent__pb2._REWARD
DESCRIPTOR.message_types_by_name['DatalogSample'] = _DATALOGSAMPLE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DatalogSample = _reflection.GeneratedProtocolMessageType('DatalogSample', (_message.Message,), dict(
  DESCRIPTOR = _DATALOGSAMPLE,
  __module__ = 'cogment.api.data_pb2'
  # @@protoc_insertion_point(class_scope:cogment.DatalogSample)
  ))
_sym_db.RegisterMessage(DatalogSample)


# @@protoc_insertion_point(module_scope)
