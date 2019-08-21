from django.utils.translation import gettext as _
from django.utils import six

from django_enumfield_named_choices.exceptions import InvalidStatusOperationError


def validate_valid_transition(enum, from_value, to_value):
    """
    Validate that to_value is a valid choice and that to_value is a valid transition from from_value.
    """
    validate_available_choice(enum, to_value)
    if hasattr(enum, "_transitions") and not enum.is_valid_transition(
        from_value, to_value
    ):
        message = _(
            six.text_type('{enum} can not go from "{from_value}" to "{to_value}"')
        )
        raise InvalidStatusOperationError(
            message.format(
                enum=enum.__name__,
                from_value=enum.name(from_value),
                to_value=enum.name(to_value) or to_value,
            )
        )


def validate_available_choice(enum, to_value):
    """
    Validate that to_value is defined as a value in enum.
    """
    if to_value is None:
        return

    if isinstance(to_value, str):
        try:
            if to_value.isdigit():
                to_value = enum.get(int(to_value)).value
            else:
                to_value = enum.get(to_value).value
        except AttributeError:
            message_str = "'{value}' cannot be found"
            message = _(six.text_type(message_str))
            raise InvalidStatusOperationError(message.format(value=to_value))

    # if to_value not in tuple(
    #     dict(list(enum.choices())).keys()
    # ) and to_value not in tuple(dict(list(enum.items())).values()):
    if to_value not in (
        tuple(dict(list(enum.choices())).keys())
        if enum.interface is not str
        else tuple(dict(list(enum.items())).values())
    ):
        message = _(
            six.text_type(
                "Select a valid choice. `{value}` is not one of the available choices."
            )
        )
        raise InvalidStatusOperationError(message.format(value=to_value))
