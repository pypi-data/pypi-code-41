# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ncbi/cloudblast/v1alpha/blast_request.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ncbi/cloudblast/v1alpha/blast_request.proto',
  package='ncbi.cloudblast.v1alpha',
  syntax='proto3',
  serialized_options=_b('\n#gov.nih.nlm.ncbi.cloudblast.v1alphaB\021BlastRequestProtoH\001P\000'),
  serialized_pb=_b('\n+ncbi/cloudblast/v1alpha/blast_request.proto\x12\x17ncbi.cloudblast.v1alpha\"3\n\x0cUserIdentity\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x12\n\nsession_id\x18\x02 \x01(\t\"\xd3\x04\n\x0c\x42lastRequest\x12\x0e\n\x06\x64\x62_tag\x18\x01 \x01(\t\x12\x16\n\x0cverbatim_seq\x18\x02 \x01(\tH\x00\x12\x17\n\rseq_accession\x18\x03 \x01(\tH\x00\x12\x31\n\x06\x63oords\x18\x08 \x01(\x0b\x32!.ncbi.cloudblast.v1alpha.SeqCoord\x12\x1a\n\x12result_bucket_name\x18\x04 \x01(\t\x12\x43\n\x07program\x18\x05 \x01(\x0e\x32\x32.ncbi.cloudblast.v1alpha.BlastRequest.BlastProgram\x12G\n\x0c\x62last_params\x18\x06 \x01(\x0b\x32\x31.ncbi.cloudblast.v1alpha.BlastRequest.BlastParams\x12\x11\n\tuser_tags\x18\x07 \x03(\t\x1a\xec\x01\n\x0b\x42lastParams\x12\x0e\n\x06\x65value\x18\x01 \x01(\x02\x12\x12\n\ngap_extend\x18\x02 \x01(\r\x12\x10\n\x08gap_open\x18\x03 \x01(\r\x12\x14\n\x0chitlist_size\x18\x04 \x01(\r\x12\x15\n\rperc_identity\x18\x05 \x01(\x02\x12\x11\n\tword_size\x18\x06 \x01(\r\x12\x13\n\x0bwindow_size\x18\x07 \x01(\r\x12\x0f\n\x07penalty\x18\x08 \x01(\x11\x12\x0e\n\x06reward\x18\t \x01(\r\x12\x31\n\x06strand\x18\n \x01(\x0e\x32!.ncbi.cloudblast.v1alpha.NAStrand\"\x1a\n\x0c\x42lastProgram\x12\n\n\x06\x42LASTN\x10\x00\x42\x07\n\x05query\"Z\n\x08SeqCoord\x12\r\n\x05start\x18\x01 \x01(\x04\x12\x0c\n\x04stop\x18\x02 \x01(\x04\x12\x31\n\x06strand\x18\x03 \x01(\x0e\x32!.ncbi.cloudblast.v1alpha.NAStrand*,\n\x08NAStrand\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x08\n\x04PLUS\x10\x01\x12\t\n\x05MINUS\x10\x02\x42<\n#gov.nih.nlm.ncbi.cloudblast.v1alphaB\x11\x42lastRequestProtoH\x01P\x00\x62\x06proto3')
)

_NASTRAND = _descriptor.EnumDescriptor(
  name='NAStrand',
  full_name='ncbi.cloudblast.v1alpha.NAStrand',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PLUS', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MINUS', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=815,
  serialized_end=859,
)
_sym_db.RegisterEnumDescriptor(_NASTRAND)

NAStrand = enum_type_wrapper.EnumTypeWrapper(_NASTRAND)
UNKNOWN = 0
PLUS = 1
MINUS = 2


_BLASTREQUEST_BLASTPROGRAM = _descriptor.EnumDescriptor(
  name='BlastProgram',
  full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastProgram',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='BLASTN', index=0, number=0,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=686,
  serialized_end=712,
)
_sym_db.RegisterEnumDescriptor(_BLASTREQUEST_BLASTPROGRAM)


_USERIDENTITY = _descriptor.Descriptor(
  name='UserIdentity',
  full_name='ncbi.cloudblast.v1alpha.UserIdentity',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user_id', full_name='ncbi.cloudblast.v1alpha.UserIdentity.user_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='session_id', full_name='ncbi.cloudblast.v1alpha.UserIdentity.session_id', index=1,
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
  serialized_start=72,
  serialized_end=123,
)


_BLASTREQUEST_BLASTPARAMS = _descriptor.Descriptor(
  name='BlastParams',
  full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='evalue', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.evalue', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gap_extend', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.gap_extend', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gap_open', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.gap_open', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hitlist_size', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.hitlist_size', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='perc_identity', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.perc_identity', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='word_size', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.word_size', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='window_size', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.window_size', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='penalty', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.penalty', index=7,
      number=8, type=17, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reward', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.reward', index=8,
      number=9, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='strand', full_name='ncbi.cloudblast.v1alpha.BlastRequest.BlastParams.strand', index=9,
      number=10, type=14, cpp_type=8, label=1,
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
  serialized_start=448,
  serialized_end=684,
)

_BLASTREQUEST = _descriptor.Descriptor(
  name='BlastRequest',
  full_name='ncbi.cloudblast.v1alpha.BlastRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='db_tag', full_name='ncbi.cloudblast.v1alpha.BlastRequest.db_tag', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='verbatim_seq', full_name='ncbi.cloudblast.v1alpha.BlastRequest.verbatim_seq', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='seq_accession', full_name='ncbi.cloudblast.v1alpha.BlastRequest.seq_accession', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='coords', full_name='ncbi.cloudblast.v1alpha.BlastRequest.coords', index=3,
      number=8, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='result_bucket_name', full_name='ncbi.cloudblast.v1alpha.BlastRequest.result_bucket_name', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='program', full_name='ncbi.cloudblast.v1alpha.BlastRequest.program', index=5,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='blast_params', full_name='ncbi.cloudblast.v1alpha.BlastRequest.blast_params', index=6,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='user_tags', full_name='ncbi.cloudblast.v1alpha.BlastRequest.user_tags', index=7,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_BLASTREQUEST_BLASTPARAMS, ],
  enum_types=[
    _BLASTREQUEST_BLASTPROGRAM,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='query', full_name='ncbi.cloudblast.v1alpha.BlastRequest.query',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=126,
  serialized_end=721,
)


_SEQCOORD = _descriptor.Descriptor(
  name='SeqCoord',
  full_name='ncbi.cloudblast.v1alpha.SeqCoord',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='start', full_name='ncbi.cloudblast.v1alpha.SeqCoord.start', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='stop', full_name='ncbi.cloudblast.v1alpha.SeqCoord.stop', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='strand', full_name='ncbi.cloudblast.v1alpha.SeqCoord.strand', index=2,
      number=3, type=14, cpp_type=8, label=1,
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
  serialized_start=723,
  serialized_end=813,
)

_BLASTREQUEST_BLASTPARAMS.fields_by_name['strand'].enum_type = _NASTRAND
_BLASTREQUEST_BLASTPARAMS.containing_type = _BLASTREQUEST
_BLASTREQUEST.fields_by_name['coords'].message_type = _SEQCOORD
_BLASTREQUEST.fields_by_name['program'].enum_type = _BLASTREQUEST_BLASTPROGRAM
_BLASTREQUEST.fields_by_name['blast_params'].message_type = _BLASTREQUEST_BLASTPARAMS
_BLASTREQUEST_BLASTPROGRAM.containing_type = _BLASTREQUEST
_BLASTREQUEST.oneofs_by_name['query'].fields.append(
  _BLASTREQUEST.fields_by_name['verbatim_seq'])
_BLASTREQUEST.fields_by_name['verbatim_seq'].containing_oneof = _BLASTREQUEST.oneofs_by_name['query']
_BLASTREQUEST.oneofs_by_name['query'].fields.append(
  _BLASTREQUEST.fields_by_name['seq_accession'])
_BLASTREQUEST.fields_by_name['seq_accession'].containing_oneof = _BLASTREQUEST.oneofs_by_name['query']
_SEQCOORD.fields_by_name['strand'].enum_type = _NASTRAND
DESCRIPTOR.message_types_by_name['UserIdentity'] = _USERIDENTITY
DESCRIPTOR.message_types_by_name['BlastRequest'] = _BLASTREQUEST
DESCRIPTOR.message_types_by_name['SeqCoord'] = _SEQCOORD
DESCRIPTOR.enum_types_by_name['NAStrand'] = _NASTRAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

UserIdentity = _reflection.GeneratedProtocolMessageType('UserIdentity', (_message.Message,), dict(
  DESCRIPTOR = _USERIDENTITY,
  __module__ = 'ncbi.cloudblast.v1alpha.blast_request_pb2'
  # @@protoc_insertion_point(class_scope:ncbi.cloudblast.v1alpha.UserIdentity)
  ))
_sym_db.RegisterMessage(UserIdentity)

BlastRequest = _reflection.GeneratedProtocolMessageType('BlastRequest', (_message.Message,), dict(

  BlastParams = _reflection.GeneratedProtocolMessageType('BlastParams', (_message.Message,), dict(
    DESCRIPTOR = _BLASTREQUEST_BLASTPARAMS,
    __module__ = 'ncbi.cloudblast.v1alpha.blast_request_pb2'
    # @@protoc_insertion_point(class_scope:ncbi.cloudblast.v1alpha.BlastRequest.BlastParams)
    ))
  ,
  DESCRIPTOR = _BLASTREQUEST,
  __module__ = 'ncbi.cloudblast.v1alpha.blast_request_pb2'
  # @@protoc_insertion_point(class_scope:ncbi.cloudblast.v1alpha.BlastRequest)
  ))
_sym_db.RegisterMessage(BlastRequest)
_sym_db.RegisterMessage(BlastRequest.BlastParams)

SeqCoord = _reflection.GeneratedProtocolMessageType('SeqCoord', (_message.Message,), dict(
  DESCRIPTOR = _SEQCOORD,
  __module__ = 'ncbi.cloudblast.v1alpha.blast_request_pb2'
  # @@protoc_insertion_point(class_scope:ncbi.cloudblast.v1alpha.SeqCoord)
  ))
_sym_db.RegisterMessage(SeqCoord)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
