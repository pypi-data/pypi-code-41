# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorboard/compat/proto/function.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorboard.compat.proto import attr_value_pb2 as tensorboard_dot_compat_dot_proto_dot_attr__value__pb2
from tensorboard.compat.proto import node_def_pb2 as tensorboard_dot_compat_dot_proto_dot_node__def__pb2
from tensorboard.compat.proto import op_def_pb2 as tensorboard_dot_compat_dot_proto_dot_op__def__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorboard/compat/proto/function.proto',
  package='tensorboard',
  syntax='proto3',
  serialized_options=_b('\n\030org.tensorflow.frameworkB\016FunctionProtosP\001Z=github.com/tensorflow/tensorflow/tensorflow/go/core/framework\370\001\001'),
  serialized_pb=_b('\n\'tensorboard/compat/proto/function.proto\x12\x0btensorboard\x1a)tensorboard/compat/proto/attr_value.proto\x1a\'tensorboard/compat/proto/node_def.proto\x1a%tensorboard/compat/proto/op_def.proto\"l\n\x12\x46unctionDefLibrary\x12*\n\x08\x66unction\x18\x01 \x03(\x0b\x32\x18.tensorboard.FunctionDef\x12*\n\x08gradient\x18\x02 \x03(\x0b\x32\x18.tensorboard.GradientDef\"\xc0\x05\n\x0b\x46unctionDef\x12%\n\tsignature\x18\x01 \x01(\x0b\x32\x12.tensorboard.OpDef\x12\x30\n\x04\x61ttr\x18\x05 \x03(\x0b\x32\".tensorboard.FunctionDef.AttrEntry\x12\x37\n\x08\x61rg_attr\x18\x07 \x03(\x0b\x32%.tensorboard.FunctionDef.ArgAttrEntry\x12&\n\x08node_def\x18\x03 \x03(\x0b\x32\x14.tensorboard.NodeDef\x12.\n\x03ret\x18\x04 \x03(\x0b\x32!.tensorboard.FunctionDef.RetEntry\x12=\n\x0b\x63ontrol_ret\x18\x06 \x03(\x0b\x32(.tensorboard.FunctionDef.ControlRetEntry\x1a\x43\n\tAttrEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.tensorboard.AttrValue:\x02\x38\x01\x1a\x8a\x01\n\x08\x41rgAttrs\x12\x39\n\x04\x61ttr\x18\x01 \x03(\x0b\x32+.tensorboard.FunctionDef.ArgAttrs.AttrEntry\x1a\x43\n\tAttrEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.tensorboard.AttrValue:\x02\x38\x01\x1aQ\n\x0c\x41rgAttrEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32!.tensorboard.FunctionDef.ArgAttrs:\x02\x38\x01\x1a*\n\x08RetEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a\x31\n\x0f\x43ontrolRetEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01J\x04\x08\x02\x10\x03\";\n\x0bGradientDef\x12\x15\n\rfunction_name\x18\x01 \x01(\t\x12\x15\n\rgradient_func\x18\x02 \x01(\tBn\n\x18org.tensorflow.frameworkB\x0e\x46unctionProtosP\x01Z=github.com/tensorflow/tensorflow/tensorflow/go/core/framework\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorboard_dot_compat_dot_proto_dot_attr__value__pb2.DESCRIPTOR,tensorboard_dot_compat_dot_proto_dot_node__def__pb2.DESCRIPTOR,tensorboard_dot_compat_dot_proto_dot_op__def__pb2.DESCRIPTOR,])




_FUNCTIONDEFLIBRARY = _descriptor.Descriptor(
  name='FunctionDefLibrary',
  full_name='tensorboard.FunctionDefLibrary',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='function', full_name='tensorboard.FunctionDefLibrary.function', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gradient', full_name='tensorboard.FunctionDefLibrary.gradient', index=1,
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
  serialized_start=179,
  serialized_end=287,
)


_FUNCTIONDEF_ATTRENTRY = _descriptor.Descriptor(
  name='AttrEntry',
  full_name='tensorboard.FunctionDef.AttrEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorboard.FunctionDef.AttrEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorboard.FunctionDef.AttrEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=602,
  serialized_end=669,
)

_FUNCTIONDEF_ARGATTRS_ATTRENTRY = _descriptor.Descriptor(
  name='AttrEntry',
  full_name='tensorboard.FunctionDef.ArgAttrs.AttrEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorboard.FunctionDef.ArgAttrs.AttrEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorboard.FunctionDef.ArgAttrs.AttrEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=602,
  serialized_end=669,
)

_FUNCTIONDEF_ARGATTRS = _descriptor.Descriptor(
  name='ArgAttrs',
  full_name='tensorboard.FunctionDef.ArgAttrs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='attr', full_name='tensorboard.FunctionDef.ArgAttrs.attr', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FUNCTIONDEF_ARGATTRS_ATTRENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=672,
  serialized_end=810,
)

_FUNCTIONDEF_ARGATTRENTRY = _descriptor.Descriptor(
  name='ArgAttrEntry',
  full_name='tensorboard.FunctionDef.ArgAttrEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorboard.FunctionDef.ArgAttrEntry.key', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorboard.FunctionDef.ArgAttrEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=812,
  serialized_end=893,
)

_FUNCTIONDEF_RETENTRY = _descriptor.Descriptor(
  name='RetEntry',
  full_name='tensorboard.FunctionDef.RetEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorboard.FunctionDef.RetEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorboard.FunctionDef.RetEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=895,
  serialized_end=937,
)

_FUNCTIONDEF_CONTROLRETENTRY = _descriptor.Descriptor(
  name='ControlRetEntry',
  full_name='tensorboard.FunctionDef.ControlRetEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorboard.FunctionDef.ControlRetEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorboard.FunctionDef.ControlRetEntry.value', index=1,
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
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=939,
  serialized_end=988,
)

_FUNCTIONDEF = _descriptor.Descriptor(
  name='FunctionDef',
  full_name='tensorboard.FunctionDef',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='signature', full_name='tensorboard.FunctionDef.signature', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='attr', full_name='tensorboard.FunctionDef.attr', index=1,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='arg_attr', full_name='tensorboard.FunctionDef.arg_attr', index=2,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node_def', full_name='tensorboard.FunctionDef.node_def', index=3,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ret', full_name='tensorboard.FunctionDef.ret', index=4,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='control_ret', full_name='tensorboard.FunctionDef.control_ret', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_FUNCTIONDEF_ATTRENTRY, _FUNCTIONDEF_ARGATTRS, _FUNCTIONDEF_ARGATTRENTRY, _FUNCTIONDEF_RETENTRY, _FUNCTIONDEF_CONTROLRETENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=290,
  serialized_end=994,
)


_GRADIENTDEF = _descriptor.Descriptor(
  name='GradientDef',
  full_name='tensorboard.GradientDef',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='function_name', full_name='tensorboard.GradientDef.function_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gradient_func', full_name='tensorboard.GradientDef.gradient_func', index=1,
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
  serialized_start=996,
  serialized_end=1055,
)

_FUNCTIONDEFLIBRARY.fields_by_name['function'].message_type = _FUNCTIONDEF
_FUNCTIONDEFLIBRARY.fields_by_name['gradient'].message_type = _GRADIENTDEF
_FUNCTIONDEF_ATTRENTRY.fields_by_name['value'].message_type = tensorboard_dot_compat_dot_proto_dot_attr__value__pb2._ATTRVALUE
_FUNCTIONDEF_ATTRENTRY.containing_type = _FUNCTIONDEF
_FUNCTIONDEF_ARGATTRS_ATTRENTRY.fields_by_name['value'].message_type = tensorboard_dot_compat_dot_proto_dot_attr__value__pb2._ATTRVALUE
_FUNCTIONDEF_ARGATTRS_ATTRENTRY.containing_type = _FUNCTIONDEF_ARGATTRS
_FUNCTIONDEF_ARGATTRS.fields_by_name['attr'].message_type = _FUNCTIONDEF_ARGATTRS_ATTRENTRY
_FUNCTIONDEF_ARGATTRS.containing_type = _FUNCTIONDEF
_FUNCTIONDEF_ARGATTRENTRY.fields_by_name['value'].message_type = _FUNCTIONDEF_ARGATTRS
_FUNCTIONDEF_ARGATTRENTRY.containing_type = _FUNCTIONDEF
_FUNCTIONDEF_RETENTRY.containing_type = _FUNCTIONDEF
_FUNCTIONDEF_CONTROLRETENTRY.containing_type = _FUNCTIONDEF
_FUNCTIONDEF.fields_by_name['signature'].message_type = tensorboard_dot_compat_dot_proto_dot_op__def__pb2._OPDEF
_FUNCTIONDEF.fields_by_name['attr'].message_type = _FUNCTIONDEF_ATTRENTRY
_FUNCTIONDEF.fields_by_name['arg_attr'].message_type = _FUNCTIONDEF_ARGATTRENTRY
_FUNCTIONDEF.fields_by_name['node_def'].message_type = tensorboard_dot_compat_dot_proto_dot_node__def__pb2._NODEDEF
_FUNCTIONDEF.fields_by_name['ret'].message_type = _FUNCTIONDEF_RETENTRY
_FUNCTIONDEF.fields_by_name['control_ret'].message_type = _FUNCTIONDEF_CONTROLRETENTRY
DESCRIPTOR.message_types_by_name['FunctionDefLibrary'] = _FUNCTIONDEFLIBRARY
DESCRIPTOR.message_types_by_name['FunctionDef'] = _FUNCTIONDEF
DESCRIPTOR.message_types_by_name['GradientDef'] = _GRADIENTDEF
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

FunctionDefLibrary = _reflection.GeneratedProtocolMessageType('FunctionDefLibrary', (_message.Message,), dict(
  DESCRIPTOR = _FUNCTIONDEFLIBRARY,
  __module__ = 'tensorboard.compat.proto.function_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.FunctionDefLibrary)
  ))
_sym_db.RegisterMessage(FunctionDefLibrary)

FunctionDef = _reflection.GeneratedProtocolMessageType('FunctionDef', (_message.Message,), dict(

  AttrEntry = _reflection.GeneratedProtocolMessageType('AttrEntry', (_message.Message,), dict(
    DESCRIPTOR = _FUNCTIONDEF_ATTRENTRY,
    __module__ = 'tensorboard.compat.proto.function_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.AttrEntry)
    ))
  ,

  ArgAttrs = _reflection.GeneratedProtocolMessageType('ArgAttrs', (_message.Message,), dict(

    AttrEntry = _reflection.GeneratedProtocolMessageType('AttrEntry', (_message.Message,), dict(
      DESCRIPTOR = _FUNCTIONDEF_ARGATTRS_ATTRENTRY,
      __module__ = 'tensorboard.compat.proto.function_pb2'
      # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.ArgAttrs.AttrEntry)
      ))
    ,
    DESCRIPTOR = _FUNCTIONDEF_ARGATTRS,
    __module__ = 'tensorboard.compat.proto.function_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.ArgAttrs)
    ))
  ,

  ArgAttrEntry = _reflection.GeneratedProtocolMessageType('ArgAttrEntry', (_message.Message,), dict(
    DESCRIPTOR = _FUNCTIONDEF_ARGATTRENTRY,
    __module__ = 'tensorboard.compat.proto.function_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.ArgAttrEntry)
    ))
  ,

  RetEntry = _reflection.GeneratedProtocolMessageType('RetEntry', (_message.Message,), dict(
    DESCRIPTOR = _FUNCTIONDEF_RETENTRY,
    __module__ = 'tensorboard.compat.proto.function_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.RetEntry)
    ))
  ,

  ControlRetEntry = _reflection.GeneratedProtocolMessageType('ControlRetEntry', (_message.Message,), dict(
    DESCRIPTOR = _FUNCTIONDEF_CONTROLRETENTRY,
    __module__ = 'tensorboard.compat.proto.function_pb2'
    # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef.ControlRetEntry)
    ))
  ,
  DESCRIPTOR = _FUNCTIONDEF,
  __module__ = 'tensorboard.compat.proto.function_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.FunctionDef)
  ))
_sym_db.RegisterMessage(FunctionDef)
_sym_db.RegisterMessage(FunctionDef.AttrEntry)
_sym_db.RegisterMessage(FunctionDef.ArgAttrs)
_sym_db.RegisterMessage(FunctionDef.ArgAttrs.AttrEntry)
_sym_db.RegisterMessage(FunctionDef.ArgAttrEntry)
_sym_db.RegisterMessage(FunctionDef.RetEntry)
_sym_db.RegisterMessage(FunctionDef.ControlRetEntry)

GradientDef = _reflection.GeneratedProtocolMessageType('GradientDef', (_message.Message,), dict(
  DESCRIPTOR = _GRADIENTDEF,
  __module__ = 'tensorboard.compat.proto.function_pb2'
  # @@protoc_insertion_point(class_scope:tensorboard.GradientDef)
  ))
_sym_db.RegisterMessage(GradientDef)


DESCRIPTOR._options = None
_FUNCTIONDEF_ATTRENTRY._options = None
_FUNCTIONDEF_ARGATTRS_ATTRENTRY._options = None
_FUNCTIONDEF_ARGATTRENTRY._options = None
_FUNCTIONDEF_RETENTRY._options = None
_FUNCTIONDEF_CONTROLRETENTRY._options = None
# @@protoc_insertion_point(module_scope)
