from django.utils import timezone

from marshmallow import ValidationError, fields, utils

from . import exceptions, schema


OMIT = object()


class Field(fields.Field):
    """Custom field only to be used when parsing `query_params`.

    :param str param_name: Optional field that defines the name of the query parameter,
     it's set as optional because parsing lists do not require a name.
    :param any default: Optional
    :param bool many: Optional
    """

    @classmethod
    def __new__(cls, *args, **kwargs):
        if issubclass(cls, Nested):
            return super().__new__(cls)

        elif kwargs.pop("many", False):
            transform = kwargs.pop("transform", None)
            return _List(cls_or_instance=cls(transform=transform, **kwargs), **kwargs)

        return super().__new__(cls)

    def __init__(
        self,
        param_name=None,
        default=utils.missing,
        allow_none=False,
        validate=None,
        many=utils.missing,
        transform=None,
        **kwargs,
    ):

        kwargs.update(
            {
                "allow_none": allow_none,
                "required": default is utils.missing,
                "validate": validate,
            }
        )

        if isinstance(self, Nested):
            kwargs["many"] = many
        elif many is not utils.missing:
            raise TypeError(
                "many should never be passed into __init__, it's only there to make mypy happy"
            )

        if param_name is not None:
            kwargs["data_key"] = param_name

        if default is not utils.missing and default is not OMIT:
            kwargs["missing"] = default

        self.transform = transform

        super().__init__(**kwargs)

    def deserialize(self, value, attr=None, data=None, **kwargs):
        if self.transform and value is not utils.missing:
            try:
                value = self.transform(value)
            except Exception as e:
                raise exceptions.ValidationError(e)

        return super().deserialize(value, attr, data, **kwargs)


class Bool(fields.Boolean, Field):
    """Custom boolean field that supports validation."""


class DateTime(fields.DateTime, Field):
    """Custom datetime field that supports validation."""

    def _deserialize(self, value, attr, data, **kwargs):
        datetime = super()._deserialize(value, attr, data, **kwargs)
        if timezone.is_naive(datetime):
            raise exceptions.ValidationError(f"Timezone must be specified for {attr}.")

        return datetime


class Date(fields.Date, Field):
    """Custom date field that supports validation."""


class Int(fields.Integer, Field):
    """Custom int field that supports validation."""

    def __init__(self, *args, min_val=None, max_val=None, **kwargs):
        self.min_val = min_val
        self.max_val = max_val

        super().__init__(*args, **kwargs)

    def _validate_size(self, val):
        return (self.max_val is None or val <= self.max_val) and (
            self.min_val is None or val >= self.min_val
        )

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)

        if not self._validate_size(ret):
            raise exceptions.ValidationError(f"Invalid interger value for {attr}")

        return ret


class String(fields.String, Field):
    """Custom str field that supports validation."""

    def __init__(
        self, *args, allow_empty=False, max_length=None, min_length=None, **kwargs
    ):
        self.allow_empty = allow_empty

        self.max_length = max_length
        self.min_length = min_length

        super().__init__(*args, **kwargs)

    def _validate_length(self, val):
        if self.allow_empty and val == "":
            return True

        return (self.max_length is None or len(val) <= self.max_length) and (
            self.min_length is None or len(val) >= self.min_length
        )

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)

        if not self.allow_empty and ret == "":
            raise exceptions.ValidationError(f"String field cannot be empty for {attr}")

        if not self._validate_length(ret):
            raise exceptions.ValidationError(f"Invalid string length for {attr}")

        return ret


class Enum(fields.String, Field):
    def __init__(self, *args, choices=None, **kwargs):
        if choices is None:
            raise TypeError("choices must be specified")

        self.choices = choices

        super().__init__(*args, **kwargs)

    def _validate_choices(self, val):
        return val in self.choices

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)

        if not self._validate_choices(ret):
            raise exceptions.ValidationError(f"Invalid choice for {attr}")

        return ret


class _List(fields.List, Field):
    """Custom list field that supports validation."""


class UUID(fields.UUID, Field):
    """UUID field."""


class Float(fields.Float, Field):
    """Float field."""


class Decimal(fields.Decimal, Field):
    """Decimal field."""

    def __init__(self, *args, max_digits=None, min_val=None, max_val=None, **kwargs):
        self.max_digits = max_digits
        self.min_val = min_val
        self.max_val = max_val

        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        ret = super()._deserialize(value, attr, data, **kwargs)

        if not self._validate_precision(ret):
            raise exceptions.ValidationError(
                f"Invalid decimal field: Digits cannot be longer than {self.max_digits}"
            )

        if not self._validate_size(ret):
            raise exceptions.ValidationError(f"Invalid decimal value for {attr}")

        return ret

    def _validate_size(self, val):
        return (self.max_val is None or val <= self.max_val) and (
            self.min_val is None or val >= self.min_val
        )

    def _validate_precision(self, value):
        """Validate the precision of the decimal field.

        # Simplified from: rest_framework.fields.Decimal.validate_precision
        """
        sign, digittuple, exponent = value.as_tuple()

        if exponent >= 0:
            # 1234500.0
            total_digits = len(digittuple) + exponent

        elif len(digittuple) > abs(exponent):
            # 123.45
            total_digits = len(digittuple)

        else:
            # 0.001234
            total_digits = abs(exponent)

        if self.max_digits is not None and total_digits > self.max_digits:
            return False

        return True


class Time(fields.Time, Field):
    """Time field."""


class Email(fields.Email, Field):
    pass


class Nested(fields.Nested, Field):
    """Custom nested field."""

    def __init__(self, spec_or_schema, *args, **kwargs):
        self._needs_schema = False
        field_schema = schema.Schema

        if isinstance(spec_or_schema, dict):
            self.fields = spec_or_schema
            self._needs_schema = True
        else:
            self.fields = spec_or_schema().fields
            field_schema = spec_or_schema

        super().__init__(field_schema, *args, **kwargs)

    def _load(self, value, data, partial=None):
        try:
            valid_data = self.schema.load(value)
        except ValidationError as exc:
            raise ValidationError(exc.messages, valid_data=exc.valid_data)
        return valid_data

    def needs_schema(self):
        """Returns true if the field requires a schema to be set."""
        return self._needs_schema

    def bind_schema(self, nested_schema):
        """Bind the schema to the field."""
        if not self._needs_schema:
            return

        self.nested = nested_schema
        self.nested.unknown = nested_schema.unknown
        self.nested.many = self.many

        # Reset the internal schema
        self.__schema = None


class Dict(fields.Dict, Field):
    pass
