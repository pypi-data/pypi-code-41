# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: snakeskin/protos/common/common.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='snakeskin/protos/common/common.proto',
  package='common',
  syntax='proto3',
  serialized_options=_b('\n$org.hyperledger.fabric.protos.commonZ+github.com/hyperledger/fabric/protos/common'),
  serialized_pb=_b('\n$snakeskin/protos/common/common.proto\x12\x06\x63ommon\x1a\x1fgoogle/protobuf/timestamp.proto\"\x1b\n\nLastConfig\x12\r\n\x05index\x18\x01 \x01(\x04\"H\n\x08Metadata\x12\r\n\x05value\x18\x01 \x01(\x0c\x12-\n\nsignatures\x18\x02 \x03(\x0b\x32\x19.common.MetadataSignature\"@\n\x11MetadataSignature\x12\x18\n\x10signature_header\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\":\n\x06Header\x12\x16\n\x0e\x63hannel_header\x18\x01 \x01(\x0c\x12\x18\n\x10signature_header\x18\x02 \x01(\x0c\"\xb9\x01\n\rChannelHeader\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x0f\n\x07version\x18\x02 \x01(\x05\x12-\n\ttimestamp\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x12\n\nchannel_id\x18\x04 \x01(\t\x12\r\n\x05tx_id\x18\x05 \x01(\t\x12\r\n\x05\x65poch\x18\x06 \x01(\x04\x12\x11\n\textension\x18\x07 \x01(\x0c\x12\x15\n\rtls_cert_hash\x18\x08 \x01(\x0c\"1\n\x0fSignatureHeader\x12\x0f\n\x07\x63reator\x18\x01 \x01(\x0c\x12\r\n\x05nonce\x18\x02 \x01(\x0c\"7\n\x07Payload\x12\x1e\n\x06header\x18\x01 \x01(\x0b\x32\x0e.common.Header\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\".\n\x08\x45nvelope\x12\x0f\n\x07payload\x18\x01 \x01(\x0c\x12\x11\n\tsignature\x18\x02 \x01(\x0c\"v\n\x05\x42lock\x12#\n\x06header\x18\x01 \x01(\x0b\x32\x13.common.BlockHeader\x12\x1f\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x11.common.BlockData\x12\'\n\x08metadata\x18\x03 \x01(\x0b\x32\x15.common.BlockMetadata\"G\n\x0b\x42lockHeader\x12\x0e\n\x06number\x18\x01 \x01(\x04\x12\x15\n\rprevious_hash\x18\x02 \x01(\x0c\x12\x11\n\tdata_hash\x18\x03 \x01(\x0c\"\x19\n\tBlockData\x12\x0c\n\x04\x64\x61ta\x18\x01 \x03(\x0c\"!\n\rBlockMetadata\x12\x10\n\x08metadata\x18\x01 \x03(\x0c*\xc0\x01\n\x06Status\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x0c\n\x07SUCCESS\x10\xc8\x01\x12\x10\n\x0b\x42\x41\x44_REQUEST\x10\x90\x03\x12\x0e\n\tFORBIDDEN\x10\x93\x03\x12\x0e\n\tNOT_FOUND\x10\x94\x03\x12\x1d\n\x18REQUEST_ENTITY_TOO_LARGE\x10\x9d\x03\x12\x1a\n\x15INTERNAL_SERVER_ERROR\x10\xf4\x03\x12\x14\n\x0fNOT_IMPLEMENTED\x10\xf5\x03\x12\x18\n\x13SERVICE_UNAVAILABLE\x10\xf7\x03*\xca\x01\n\nHeaderType\x12\x0b\n\x07MESSAGE\x10\x00\x12\n\n\x06\x43ONFIG\x10\x01\x12\x11\n\rCONFIG_UPDATE\x10\x02\x12\x18\n\x14\x45NDORSER_TRANSACTION\x10\x03\x12\x17\n\x13ORDERER_TRANSACTION\x10\x04\x12\x15\n\x11\x44\x45LIVER_SEEK_INFO\x10\x05\x12\x15\n\x11\x43HAINCODE_PACKAGE\x10\x06\x12\x18\n\x14PEER_ADMIN_OPERATION\x10\x08\x12\x15\n\x11TOKEN_TRANSACTION\x10\t*[\n\x12\x42lockMetadataIndex\x12\x0e\n\nSIGNATURES\x10\x00\x12\x0f\n\x0bLAST_CONFIG\x10\x01\x12\x17\n\x13TRANSACTIONS_FILTER\x10\x02\x12\x0b\n\x07ORDERER\x10\x03\x42S\n$org.hyperledger.fabric.protos.commonZ+github.com/hyperledger/fabric/protos/commonb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])

_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='common.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=200,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_REQUEST', index=2, number=400,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FORBIDDEN', index=3, number=403,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NOT_FOUND', index=4, number=404,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_ENTITY_TOO_LARGE', index=5, number=413,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INTERNAL_SERVER_ERROR', index=6, number=500,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NOT_IMPLEMENTED', index=7, number=501,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SERVICE_UNAVAILABLE', index=8, number=503,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=910,
  serialized_end=1102,
)
_sym_db.RegisterEnumDescriptor(_STATUS)

Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
_HEADERTYPE = _descriptor.EnumDescriptor(
  name='HeaderType',
  full_name='common.HeaderType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='MESSAGE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONFIG', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONFIG_UPDATE', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENDORSER_TRANSACTION', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ORDERER_TRANSACTION', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DELIVER_SEEK_INFO', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CHAINCODE_PACKAGE', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PEER_ADMIN_OPERATION', index=7, number=8,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TOKEN_TRANSACTION', index=8, number=9,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1105,
  serialized_end=1307,
)
_sym_db.RegisterEnumDescriptor(_HEADERTYPE)

HeaderType = enum_type_wrapper.EnumTypeWrapper(_HEADERTYPE)
_BLOCKMETADATAINDEX = _descriptor.EnumDescriptor(
  name='BlockMetadataIndex',
  full_name='common.BlockMetadataIndex',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SIGNATURES', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='LAST_CONFIG', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRANSACTIONS_FILTER', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ORDERER', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1309,
  serialized_end=1400,
)
_sym_db.RegisterEnumDescriptor(_BLOCKMETADATAINDEX)

BlockMetadataIndex = enum_type_wrapper.EnumTypeWrapper(_BLOCKMETADATAINDEX)
UNKNOWN = 0
SUCCESS = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
REQUEST_ENTITY_TOO_LARGE = 413
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
SERVICE_UNAVAILABLE = 503
MESSAGE = 0
CONFIG = 1
CONFIG_UPDATE = 2
ENDORSER_TRANSACTION = 3
ORDERER_TRANSACTION = 4
DELIVER_SEEK_INFO = 5
CHAINCODE_PACKAGE = 6
PEER_ADMIN_OPERATION = 8
TOKEN_TRANSACTION = 9
SIGNATURES = 0
LAST_CONFIG = 1
TRANSACTIONS_FILTER = 2
ORDERER = 3



_LASTCONFIG = _descriptor.Descriptor(
  name='LastConfig',
  full_name='common.LastConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='index', full_name='common.LastConfig.index', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=81,
  serialized_end=108,
)


_METADATA = _descriptor.Descriptor(
  name='Metadata',
  full_name='common.Metadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='common.Metadata.value', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signatures', full_name='common.Metadata.signatures', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=110,
  serialized_end=182,
)


_METADATASIGNATURE = _descriptor.Descriptor(
  name='MetadataSignature',
  full_name='common.MetadataSignature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signature_header', full_name='common.MetadataSignature.signature_header', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature', full_name='common.MetadataSignature.signature', index=1,
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
  serialized_start=184,
  serialized_end=248,
)


_HEADER = _descriptor.Descriptor(
  name='Header',
  full_name='common.Header',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_header', full_name='common.Header.channel_header', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature_header', full_name='common.Header.signature_header', index=1,
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
  serialized_start=250,
  serialized_end=308,
)


_CHANNELHEADER = _descriptor.Descriptor(
  name='ChannelHeader',
  full_name='common.ChannelHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='common.ChannelHeader.type', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='common.ChannelHeader.version', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='common.ChannelHeader.timestamp', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channel_id', full_name='common.ChannelHeader.channel_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tx_id', full_name='common.ChannelHeader.tx_id', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='epoch', full_name='common.ChannelHeader.epoch', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='extension', full_name='common.ChannelHeader.extension', index=6,
      number=7, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tls_cert_hash', full_name='common.ChannelHeader.tls_cert_hash', index=7,
      number=8, type=12, cpp_type=9, label=1,
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
  serialized_start=311,
  serialized_end=496,
)


_SIGNATUREHEADER = _descriptor.Descriptor(
  name='SignatureHeader',
  full_name='common.SignatureHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='creator', full_name='common.SignatureHeader.creator', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nonce', full_name='common.SignatureHeader.nonce', index=1,
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
  serialized_start=498,
  serialized_end=547,
)


_PAYLOAD = _descriptor.Descriptor(
  name='Payload',
  full_name='common.Payload',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='common.Payload.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='common.Payload.data', index=1,
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
  serialized_start=549,
  serialized_end=604,
)


_ENVELOPE = _descriptor.Descriptor(
  name='Envelope',
  full_name='common.Envelope',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='payload', full_name='common.Envelope.payload', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature', full_name='common.Envelope.signature', index=1,
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
  serialized_start=606,
  serialized_end=652,
)


_BLOCK = _descriptor.Descriptor(
  name='Block',
  full_name='common.Block',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='common.Block.header', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='common.Block.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='common.Block.metadata', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  serialized_start=654,
  serialized_end=772,
)


_BLOCKHEADER = _descriptor.Descriptor(
  name='BlockHeader',
  full_name='common.BlockHeader',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='number', full_name='common.BlockHeader.number', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='previous_hash', full_name='common.BlockHeader.previous_hash', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_hash', full_name='common.BlockHeader.data_hash', index=2,
      number=3, type=12, cpp_type=9, label=1,
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
  serialized_start=774,
  serialized_end=845,
)


_BLOCKDATA = _descriptor.Descriptor(
  name='BlockData',
  full_name='common.BlockData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='common.BlockData.data', index=0,
      number=1, type=12, cpp_type=9, label=3,
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
  serialized_start=847,
  serialized_end=872,
)


_BLOCKMETADATA = _descriptor.Descriptor(
  name='BlockMetadata',
  full_name='common.BlockMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='metadata', full_name='common.BlockMetadata.metadata', index=0,
      number=1, type=12, cpp_type=9, label=3,
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
  serialized_start=874,
  serialized_end=907,
)

_METADATA.fields_by_name['signatures'].message_type = _METADATASIGNATURE
_CHANNELHEADER.fields_by_name['timestamp'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_PAYLOAD.fields_by_name['header'].message_type = _HEADER
_BLOCK.fields_by_name['header'].message_type = _BLOCKHEADER
_BLOCK.fields_by_name['data'].message_type = _BLOCKDATA
_BLOCK.fields_by_name['metadata'].message_type = _BLOCKMETADATA
DESCRIPTOR.message_types_by_name['LastConfig'] = _LASTCONFIG
DESCRIPTOR.message_types_by_name['Metadata'] = _METADATA
DESCRIPTOR.message_types_by_name['MetadataSignature'] = _METADATASIGNATURE
DESCRIPTOR.message_types_by_name['Header'] = _HEADER
DESCRIPTOR.message_types_by_name['ChannelHeader'] = _CHANNELHEADER
DESCRIPTOR.message_types_by_name['SignatureHeader'] = _SIGNATUREHEADER
DESCRIPTOR.message_types_by_name['Payload'] = _PAYLOAD
DESCRIPTOR.message_types_by_name['Envelope'] = _ENVELOPE
DESCRIPTOR.message_types_by_name['Block'] = _BLOCK
DESCRIPTOR.message_types_by_name['BlockHeader'] = _BLOCKHEADER
DESCRIPTOR.message_types_by_name['BlockData'] = _BLOCKDATA
DESCRIPTOR.message_types_by_name['BlockMetadata'] = _BLOCKMETADATA
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
DESCRIPTOR.enum_types_by_name['HeaderType'] = _HEADERTYPE
DESCRIPTOR.enum_types_by_name['BlockMetadataIndex'] = _BLOCKMETADATAINDEX
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LastConfig = _reflection.GeneratedProtocolMessageType('LastConfig', (_message.Message,), {
  'DESCRIPTOR' : _LASTCONFIG,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.LastConfig)
  })
_sym_db.RegisterMessage(LastConfig)

Metadata = _reflection.GeneratedProtocolMessageType('Metadata', (_message.Message,), {
  'DESCRIPTOR' : _METADATA,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.Metadata)
  })
_sym_db.RegisterMessage(Metadata)

MetadataSignature = _reflection.GeneratedProtocolMessageType('MetadataSignature', (_message.Message,), {
  'DESCRIPTOR' : _METADATASIGNATURE,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.MetadataSignature)
  })
_sym_db.RegisterMessage(MetadataSignature)

Header = _reflection.GeneratedProtocolMessageType('Header', (_message.Message,), {
  'DESCRIPTOR' : _HEADER,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.Header)
  })
_sym_db.RegisterMessage(Header)

ChannelHeader = _reflection.GeneratedProtocolMessageType('ChannelHeader', (_message.Message,), {
  'DESCRIPTOR' : _CHANNELHEADER,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.ChannelHeader)
  })
_sym_db.RegisterMessage(ChannelHeader)

SignatureHeader = _reflection.GeneratedProtocolMessageType('SignatureHeader', (_message.Message,), {
  'DESCRIPTOR' : _SIGNATUREHEADER,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.SignatureHeader)
  })
_sym_db.RegisterMessage(SignatureHeader)

Payload = _reflection.GeneratedProtocolMessageType('Payload', (_message.Message,), {
  'DESCRIPTOR' : _PAYLOAD,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.Payload)
  })
_sym_db.RegisterMessage(Payload)

Envelope = _reflection.GeneratedProtocolMessageType('Envelope', (_message.Message,), {
  'DESCRIPTOR' : _ENVELOPE,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.Envelope)
  })
_sym_db.RegisterMessage(Envelope)

Block = _reflection.GeneratedProtocolMessageType('Block', (_message.Message,), {
  'DESCRIPTOR' : _BLOCK,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.Block)
  })
_sym_db.RegisterMessage(Block)

BlockHeader = _reflection.GeneratedProtocolMessageType('BlockHeader', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKHEADER,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.BlockHeader)
  })
_sym_db.RegisterMessage(BlockHeader)

BlockData = _reflection.GeneratedProtocolMessageType('BlockData', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKDATA,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.BlockData)
  })
_sym_db.RegisterMessage(BlockData)

BlockMetadata = _reflection.GeneratedProtocolMessageType('BlockMetadata', (_message.Message,), {
  'DESCRIPTOR' : _BLOCKMETADATA,
  '__module__' : 'snakeskin.protos.common.common_pb2'
  # @@protoc_insertion_point(class_scope:common.BlockMetadata)
  })
_sym_db.RegisterMessage(BlockMetadata)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
