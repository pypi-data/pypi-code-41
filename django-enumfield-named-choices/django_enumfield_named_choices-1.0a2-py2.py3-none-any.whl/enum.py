import logging

from django.utils import six
from django.utils.encoding import python_2_unicode_compatible

from django_enumfield_named_choices.db.fields import EnumField

logger = logging.getLogger(__name__)


class EnumType(type):
    """ Custom metaclass for Enum type """

    def __new__(mcs, *args):
        """ Create enum values from all uppercase class attributes and store them in a dict on the Enum class."""
        enum = super(EnumType, mcs).__new__(mcs, *args)
        attributes = [k_v for k_v in list(enum.__dict__.items()) if k_v[0].isupper()]
        labels = enum.__dict__.get("labels", {})

        interface = enum.__dict__.get("interface", int)

        assert_arg = (
            "`" + interface.__name__ + "`"
            if isinstance(interface, type)
            else "value: `" + str(interface) + "`"
        )
        assert isinstance(interface, (type,)) and interface in (int, str), (
            f"You must set `interface` attribute of your Enum class "
            f"with one of the following types `int` or `str` instead of "
            f"{assert_arg}!"
        )

        enum.interface = interface

        enum.values = {}
        for attribute in attributes:
            enum.values[attribute[1]] = enum.Value(
                attribute[0], attribute[1], labels.get(attribute[1]), enum
            )

        return enum


class Enum(six.with_metaclass(EnumType)):
    """ A container for holding and restoring enum values """

    @python_2_unicode_compatible
    class Value(object):
        """
        A value represents a key-value pair with a uppercase name and a integer value:
        GENDER = 1
        "name" is a upper case string representing the class attribute
        "label" is a translatable human readable version of "name"
        "enum_type" is the value defined for the class attribute
        """

        def __init__(self, name, value, label, enum_type):
            self.name = name
            self.value = value
            self._label = label
            self.enum_type = enum_type

        def __str__(self):
            return six.text_type(self.label)

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other and isinstance(other, Enum.Value):
                return self.value == other.value
            elif isinstance(other, six.string_types):
                return type(other)(self.value) == other
            else:
                raise TypeError(
                    "Can not compare Enum with %s" % other.__class__.__name__
                )

        @property
        def label(self):
            return self._label or self.name

        def deconstruct(self):
            path = self.__module__ + "." + self.__class__.__name__
            return path, (self.name, self.value, self.label, self.enum_type), {}

    @classmethod
    def choices(cls, blank=False):
        """ Choices for Enum
        :return: List of tuples (<value>, <human-readable value>)
        :rtype: list
        """
        choices = list(
            (key if cls.interface is int else value.name.lower(), value)
            for key, value in cls.values.items()
        )
        # for key, value in sorted(cls.values.items(), key=lambda x: x[0]))

        if blank:
            choices.insert(0, ("", Enum.Value("", None, "", cls)))
        return choices

    @classmethod
    def default(cls):
        """ Default Enum value. Override this method if you need another default value.
        Usage:
            IntegerField(choices=my_enum.choices(), default=my_enum.default(), ...
        :return Default value, which is the first one by default.
        :rtype: int
        """
        return cls.get(cls.choices()[0][0]).value

    @classmethod
    def field(cls, **kwargs):
        """ A shortcut for field declaration
        Usage:
            class MyModelStatuses(Enum):
                UNKNOWN = 0

            class MyModel(Model):
                status = MyModelStatuses.field()

        :param kwargs: Arguments passed in EnumField.__init__()
        :rtype: EnumField
        """
        return EnumField(cls, **kwargs)

    @classmethod
    def get(cls, name_or_numeric):
        """ Get Enum.Value object matching the value argument.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :rtype: Enum.Value
        """
        if isinstance(name_or_numeric, six.string_types):
            if name_or_numeric.isdigit():
                name_or_numeric = int(name_or_numeric)
            else:
                name_or_numeric = getattr(cls, name_or_numeric.upper())

        return cls.values.get(name_or_numeric)

    @classmethod
    def name(cls, name_or_numeric):
        """ Get attribute name for the matching Enum.Value
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int
        :return: Attribute name for value
        :rtype: str
        """
        value = cls.get(name_or_numeric)
        return six.text_type(value.name) if value is not None else None

    @classmethod
    def label(cls, name_or_numeric):
        """ Get human readable label for the matching Enum.Value.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int
        :return: label for value
        :rtype: str or
        """
        value = cls.get(name_or_numeric)
        return six.text_type(value.label) if value is not None else None

    @classmethod
    def value(cls, name_or_numeric):
        """ Get human readable label for the matching Enum.Value.
        :param name_or_numeric: Integer value or attribute name
        :type name_or_numeric: int or str
        :return: label for value
        :rtype: str or
        """
        value = cls.get(name_or_numeric)
        return value.value if value is not None else None

    @classmethod
    def items(cls):
        """
        :return: List of tuples consisting of every enum value in the form [('NAME', value), ...]
        :rtype: list
        """
        items = [(value.name, key) for key, value in cls.values.items()]
        return sorted(items, key=lambda x: x[1])

    @classmethod
    def is_valid_transition(cls, from_value, to_value):
        """ Will check if to_value is a valid transition from from_value. Returns true if it is a valid transition.
        :param from_value: Start transition point
        :param to_value: End transition point
        :type from_value: int
        :type to_value: int
        :return: Success flag
        :rtype: bool
        """
        try:
            return from_value == to_value or from_value in cls.transition_origins(
                to_value
            )
        except KeyError:
            return False

    @classmethod
    def transition_origins(cls, to_value):
        """ Returns all values the to_value can make a transition from.
        :param to_value End transition point
        :type to_value: int
        :rtype: list
        """
        return cls._transitions[to_value]


Value = Enum.Value
