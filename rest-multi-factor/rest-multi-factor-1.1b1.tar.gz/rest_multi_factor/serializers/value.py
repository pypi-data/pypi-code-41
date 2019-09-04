"""Value serializer for future validations."""

__all__ = (
    "ValueSerializer",
)

from rest_framework.serializers import Serializer, CharField


class ValueSerializer(Serializer):
    """Serializer for the main value to verify."""

    update = None
    create = None

    value = CharField(write_only=True)
