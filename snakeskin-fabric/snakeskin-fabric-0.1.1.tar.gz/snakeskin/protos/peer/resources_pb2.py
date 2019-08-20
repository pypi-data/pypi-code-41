# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: snakeskin/protos/peer/resources.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from snakeskin.protos.common import configtx_pb2 as snakeskin_dot_protos_dot_common_dot_configtx__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='snakeskin/protos/peer/resources.proto',
  package='protos',
  syntax='proto3',
  serialized_options=_b('\n\"org.hyperledger.fabric.protos.peerZ)github.com/hyperledger/fabric/protos/peer'),
  serialized_pb=_b('\n%snakeskin/protos/peer/resources.proto\x12\x06protos\x1a&snakeskin/protos/common/configtx.proto\"4\n\x13\x43haincodeIdentifier\x12\x0c\n\x04hash\x18\x01 \x01(\x0c\x12\x0f\n\x07version\x18\x02 \x01(\t\"5\n\x13\x43haincodeValidation\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x61rgument\x18\x02 \x01(\x0c\"*\n\x08VSCCArgs\x12\x1e\n\x16\x65ndorsement_policy_ref\x18\x01 \x01(\t\"$\n\x14\x43haincodeEndorsement\x12\x0c\n\x04name\x18\x01 \x01(\t\"^\n\nConfigTree\x12&\n\x0e\x63hannel_config\x18\x01 \x01(\x0b\x32\x0e.common.Config\x12(\n\x10resources_config\x18\x02 \x01(\x0b\x32\x0e.common.ConfigBO\n\"org.hyperledger.fabric.protos.peerZ)github.com/hyperledger/fabric/protos/peerb\x06proto3')
  ,
  dependencies=[snakeskin_dot_protos_dot_common_dot_configtx__pb2.DESCRIPTOR,])




_CHAINCODEIDENTIFIER = _descriptor.Descriptor(
  name='ChaincodeIdentifier',
  full_name='protos.ChaincodeIdentifier',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='hash', full_name='protos.ChaincodeIdentifier.hash', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='protos.ChaincodeIdentifier.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=89,
  serialized_end=141,
)


_CHAINCODEVALIDATION = _descriptor.Descriptor(
  name='ChaincodeValidation',
  full_name='protos.ChaincodeValidation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='protos.ChaincodeValidation.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='argument', full_name='protos.ChaincodeValidation.argument', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
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
  serialized_start=143,
  serialized_end=196,
)


_VSCCARGS = _descriptor.Descriptor(
  name='VSCCArgs',
  full_name='protos.VSCCArgs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='endorsement_policy_ref', full_name='protos.VSCCArgs.endorsement_policy_ref', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=198,
  serialized_end=240,
)


_CHAINCODEENDORSEMENT = _descriptor.Descriptor(
  name='ChaincodeEndorsement',
  full_name='protos.ChaincodeEndorsement',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='protos.ChaincodeEndorsement.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=242,
  serialized_end=278,
)


_CONFIGTREE = _descriptor.Descriptor(
  name='ConfigTree',
  full_name='protos.ConfigTree',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_config', full_name='protos.ConfigTree.channel_config', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resources_config', full_name='protos.ConfigTree.resources_config', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=280,
  serialized_end=374,
)

_CONFIGTREE.fields_by_name['channel_config'].message_type = snakeskin_dot_protos_dot_common_dot_configtx__pb2._CONFIG
_CONFIGTREE.fields_by_name['resources_config'].message_type = snakeskin_dot_protos_dot_common_dot_configtx__pb2._CONFIG
DESCRIPTOR.message_types_by_name['ChaincodeIdentifier'] = _CHAINCODEIDENTIFIER
DESCRIPTOR.message_types_by_name['ChaincodeValidation'] = _CHAINCODEVALIDATION
DESCRIPTOR.message_types_by_name['VSCCArgs'] = _VSCCARGS
DESCRIPTOR.message_types_by_name['ChaincodeEndorsement'] = _CHAINCODEENDORSEMENT
DESCRIPTOR.message_types_by_name['ConfigTree'] = _CONFIGTREE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ChaincodeIdentifier = _reflection.GeneratedProtocolMessageType('ChaincodeIdentifier', (_message.Message,), {
  'DESCRIPTOR' : _CHAINCODEIDENTIFIER,
  '__module__' : 'snakeskin.protos.peer.resources_pb2'
  # @@protoc_insertion_point(class_scope:protos.ChaincodeIdentifier)
  })
_sym_db.RegisterMessage(ChaincodeIdentifier)

ChaincodeValidation = _reflection.GeneratedProtocolMessageType('ChaincodeValidation', (_message.Message,), {
  'DESCRIPTOR' : _CHAINCODEVALIDATION,
  '__module__' : 'snakeskin.protos.peer.resources_pb2'
  # @@protoc_insertion_point(class_scope:protos.ChaincodeValidation)
  })
_sym_db.RegisterMessage(ChaincodeValidation)

VSCCArgs = _reflection.GeneratedProtocolMessageType('VSCCArgs', (_message.Message,), {
  'DESCRIPTOR' : _VSCCARGS,
  '__module__' : 'snakeskin.protos.peer.resources_pb2'
  # @@protoc_insertion_point(class_scope:protos.VSCCArgs)
  })
_sym_db.RegisterMessage(VSCCArgs)

ChaincodeEndorsement = _reflection.GeneratedProtocolMessageType('ChaincodeEndorsement', (_message.Message,), {
  'DESCRIPTOR' : _CHAINCODEENDORSEMENT,
  '__module__' : 'snakeskin.protos.peer.resources_pb2'
  # @@protoc_insertion_point(class_scope:protos.ChaincodeEndorsement)
  })
_sym_db.RegisterMessage(ChaincodeEndorsement)

ConfigTree = _reflection.GeneratedProtocolMessageType('ConfigTree', (_message.Message,), {
  'DESCRIPTOR' : _CONFIGTREE,
  '__module__' : 'snakeskin.protos.peer.resources_pb2'
  # @@protoc_insertion_point(class_scope:protos.ConfigTree)
  })
_sym_db.RegisterMessage(ConfigTree)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
