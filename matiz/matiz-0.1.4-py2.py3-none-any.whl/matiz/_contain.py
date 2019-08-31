import dataclasses
import logging
import typing

from . import _common

_logger = logging.getLogger(__name__)
MISSING = dataclasses.MISSING
MissingOrAny = typing.Union[type(MISSING), typing.Any]


class DataclassFieldMeta(type):

    def __init__(cls, name, bases, attrs):
        if '__dataclass_fields__' not in attrs:
            msg = f"Matiz class {name!r} must be a dataclass. Use `dataclass` decorator."
            _logger.error(msg)
            print(f"\nError: Not a dataclass. {msg}")
        super(DataclassFieldMeta, cls).__init__(name, bases, attrs)


class Containable(metaclass=DataclassFieldMeta):
    """Intended to represent mapping type container.

    key is a valid python identifier
    value is derived from ValidableField
    """

    represent_as_mapping = True

    def as_dict(self):
        fields_names = {f.name for f in dataclasses.fields(self)}
        return {k: v for k, v in self.__dict__.items() if k in fields_names}

    def dataclass_items(self):
        return get_dataclass_items(self)

    def traverse(self, path=None):
        path = path or self.__class__.__name__
        for i, (descriptor, attribute) in self.dataclass_items():
            if is_represented_as_mapping(self):
                sub_path = f"{path}.{descriptor.name}"
            else:
                sub_path = f"{path}[{i}]"

            if is_containable(attribute):
                yield from attribute.traverse(sub_path)
            else:
                yield descriptor.name, sub_path, attribute

    @classmethod
    def from_dict(cls, arbitrary_kwargs):
        assert isinstance(arbitrary_kwargs, dict), f"Bad type: {type(arbitrary_kwargs)}."
        native_kwargs = {}
        for f in dataclasses.fields(cls):
            if f.name in arbitrary_kwargs:
                native_kwargs[f.name] = arbitrary_kwargs.pop(f.name)
        object_ = cls(**native_kwargs)
        object_.aux_call_kwargs = arbitrary_kwargs
        return object_

    @classmethod
    def from_list(cls, arbitrary_kwargs):
        assert isinstance(arbitrary_kwargs, dict), f"Bad type: {type(arbitrary_kwargs)}."
        native_kwargs = {}
        for f in dataclasses.fields(cls):
            if f.name in arbitrary_kwargs:
                native_kwargs[f.name] = arbitrary_kwargs.pop(f.name)
        object_ = cls(**native_kwargs)
        object_.aux_call_kwargs = arbitrary_kwargs
        return object_


def is_containable(obj):
    return dataclasses.is_dataclass(obj)


def is_represented_as_mapping(obj):
    return is_containable(obj) and getattr(obj, 'represent_as_mapping', None)


def get_dataclass_items(object_) -> typing.Generator[typing.Tuple, None, None]:
    if is_containable(object_):
        yield from zip(dataclasses.fields(object_), dataclasses.astuple(object_))
    else:
        _logger.error(f"Cannot use {type(object_).__name__} as a dataclass.")


class ContainFieldBase(dataclasses.Field):
    def __init__(
            self,  # use `default` for scalars (or any immutable type)
            default: MissingOrAny = MISSING,
            # or `default_factory` for mutable kinds, like collections.
            # It has to be callable being a default constructor in C++' meaning.
            default_factory: MissingOrAny = MISSING,

            # use those below to tell dataclasses if this field has to be used in generation
            # of corresponding methods of parent container (refer to `dataclass.field()` docs).
            init: bool = True,
            repr_: bool = True,
            hash_: bool = None,
            compare: bool = True,
            metadata: typing.Any = None,
    ):

        if default is not MISSING and default_factory is not MISSING:
            raise ValueError('Cannot specify both default and default_factory.')
        super().__init__(default, default_factory, init, repr_, hash_, compare, metadata)

    def get_default(self):
        if self.default_factory is not MISSING:
            try:
                return self.default_factory()
            except (TypeError, ValueError, AttributeError) as e:
                msg = f"default_factory failed: {type(e).__name__}: {e}."
                _logger.error(msg)
                return self.default_factory

        if self.default is not MISSING:
            return self.default
        msg = f"Unable to get_default() for field {type(self).__name__}.{self.name}."
        if not self.default_factory:
            msg += f" Neither `default` nor `default_factory` attribute defined."
        raise TypeError(msg)

    def __repr__(self):
        return f"{self.__class__.__name__}(...)"


def unused__call__(cls, *unknown_args, **unknown_kwargs):
    native_args = []
    native_kwargs = {}
    positional_fields_consumed = set()
    unknown_args = list(unknown_args)

    _common.trace_call(cls, unknown_args, unknown_kwargs, f"\nclass {cls.__name__}:\noriginal")

    for i, field in enumerate(dataclasses.fields(cls)):
        if field.name in {'aux_call_args', 'aux_call_kwargs'}:
            continue
        if i < len(unknown_args):
            native_args.append(unknown_args.pop(0))
            positional_fields_consumed.add(field.name)
        elif field.name in unknown_kwargs:
            duplication_msg = f"Duplicated values for argument {field.name}."
            assert field.name not in positional_fields_consumed, duplication_msg
            assert field.name not in native_kwargs, duplication_msg
            assert field.name != 'aux_call_kwargs', f"Bad call-arguments propagation in {cls.__name__}."
            native_kwargs[field.name] = unknown_kwargs.pop(field.name)
        else:
            native_kwargs[field.name] = field.get_default()

    native_kwargs['aux_call_args'] = unknown_args
    native_kwargs['aux_call_kwargs'] = unknown_kwargs
    _common.trace_call(cls, native_args, native_kwargs, "native", logger=_logger)

    instance = super().__call__(*native_args, **native_kwargs)
    return instance
