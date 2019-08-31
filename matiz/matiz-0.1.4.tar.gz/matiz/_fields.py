# pylint: disable=not-callable

import functools
import logging
import typing

from . import _contain, _valid

_logger = logging.getLogger(__name__)


class ValidableField(_contain.ContainFieldBase):
    """Specifies details of own dataclasses.Field object."""

    iz_validators = None

    def __init__(self, mandatory: bool = False, description: typing.Optional[str] = None, **kwargs):
        self.mandatory = mandatory
        self.description = description
        super().__init__(**kwargs)

    def violations(self, py_value, path_) -> typing.Generator:
        if self.mandatory and py_value is _contain.MISSING:
            yield _valid.Violation(path_, "Mandatory value is missing.")


class TObject(ValidableField):

    def __init__(self, default_constructor: typing.Callable, **kwargs):
        super().__init__(default_factory=default_constructor, **kwargs)


class TList(ValidableField):

    def __init__(
            self,
            default_factory: ValidableField,
            *,
            min_len=None,
            max_len=None,
            **kwargs,
    ):
        super().__init__(default_factory=default_factory, **kwargs)
        self.min_len = min_len
        self.max_len = max_len

    def violations(self, py_value, path) -> typing.Generator[_valid.Violation, None, None]:
        yield from super().violations(py_value, path)
        for index, item in enumerate(py_value):
            print(f"self.default_factory: {self.default_factory}")
            if hasattr(self.default_factory, 'violations'):
                yield from self.default_factory.violations(item, f"{path}[{index}]")
            else:
                print("Cannot validate")


class TString(ValidableField):
    default = ''

    def __init__(self, min_len=None, max_len=None, **other_args):
        self.length_range = _valid.RangeValidator(min_len, max_len)
        if 'default' not in other_args:
            other_args['default'] = self.__class__.default

        super().__init__(**other_args)

    def violations(self, py_value, path) -> typing.Generator:
        yield from super().violations(py_value, path)
        yield from self.length_range.validate(len(str(py_value)), path)


class TInt(ValidableField):
    minimum = None
    maximum = None
    signed = False
    default = 0

    def __init__(self, minimum=None, maximum=None, **other_args):
        if minimum is None:
            minimum = self.minimum
        if maximum is None:
            maximum = self.maximum
        if 'default' not in other_args:
            other_args['default'] = self.__class__.default

        self.value_range = _valid.RangeValidator(minimum, maximum)
        super().__init__(**other_args)

    def violations(self, py_value, path) -> typing.Generator[_valid.Violation, None, None]:
        print(f"checking violations {self.__class__.__name__}: {path}")
        yield from super().violations(py_value, path)
        yield from self.value_range.validate(py_value, path)


def _make_int_type(signed, bits_length):
    bytes_num, reminder = divmod(bits_length, 8)
    assert not reminder, "Number of bits has to be a multiply of 8"
    full = 2 ** bits_length

    def wrapper(cls):
        if signed:
            cls.minimum = -1 * full / 2
            cls.maximum = -1 + full / 2
        else:
            cls.minimum = 0
            cls.maximum = - 1 + full

        return cls

    return wrapper


_unsigned = functools.partial(_make_int_type, False)
_signed = functools.partial(_make_int_type, True)


@_unsigned(8)
class TUInt8(TInt):
    pass


@_unsigned(16)
class TUInt16(TInt):
    pass


@_unsigned(32)
class TUInt32(TInt):
    pass


@_unsigned(64)
class TUInt64(TInt):
    pass


@_signed(8)
class TInt8(TInt):
    pass


@_signed(16)
class TInt16(TInt):
    pass


@_signed(32)
class TInt32(TInt):
    pass


@_signed(64)
class TInt64(TInt):
    pass
